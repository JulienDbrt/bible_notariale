import os
import logging
import asyncio
import time
from typing import List, Dict, Any, Optional, Union
from neo4j import AsyncGraphDatabase
from neo4j.exceptions import ServiceUnavailable, TransientError
from ..core.config import settings

logger = logging.getLogger(__name__)

class Neo4jService:
    def __init__(self) -> None:
        self.driver: Optional[Any] = None
        self.uri = os.getenv("NEO4J_URL", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
    
    async def initialize(self) -> None:
        """Initialize Neo4j connection and setup indexes"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            
            # Test connection with timeout
            try:
                if self.driver:
                    await asyncio.wait_for(self.driver.verify_connectivity(), timeout=10.0)
                logger.info("✅ Neo4j connection established")
            except asyncio.TimeoutError:
                logger.warning("⚠️ Neo4j connectivity timeout - proceeding anyway")
            
            # Setup vector index for embeddings
            await self._setup_vector_index()

            # Setup full-text index for lexical search
            await self._setup_fulltext_index()

        except Exception as e:
            logger.error(f"Failed to initialize Neo4j: {e}")
            raise e
    
    async def _setup_vector_index(self) -> None:
        """Setup vector index for chunk embeddings"""
        if not self.driver:
            logger.error("Neo4j driver not initialized.")
            return

        # Récupérer les dimensions depuis les variables d'environnement
        embedding_dimensions = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))

        async with self.driver.session() as session:
            try:
                # Create vector index for chunk embeddings
                await session.run("""
                    CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
                    FOR (c:Chunk) ON (c.embedding)
                    OPTIONS {indexConfig: {
                        `vector.dimensions`: $dimensions,
                        `vector.similarity_function`: 'cosine'
                    }}
                """, dimensions=embedding_dimensions)
                logger.info(f"Vector index for chunks created/verified (dimensions: {embedding_dimensions})")
            except Exception as e:
                logger.warning(f"Vector index setup issue (may already exist): {e}")

    async def _setup_fulltext_index(self) -> None:
        """Crée un index full-text sur le contenu des chunks."""
        if not self.driver:
            logger.error("Neo4j driver not initialized.")
            return
        async with self.driver.session() as session:
            try:
                await session.run("""
                    CREATE FULLTEXT INDEX chunk_text_index IF NOT EXISTS
                    FOR (c:Chunk) ON EACH [c.text]
                """)
                logger.info("Full-text index for chunks created/verified")
            except Exception as e:
                logger.warning(f"Full-text index setup issue (may already exist): {e}")
    
    async def _run_with_retry(self, query_func: Any, *args: Any, **kwargs: Any) -> Any:
        """NOUVELLE FONCTION : Exécute une fonction de session avec re-tentatives."""
        if not self.driver:
            logger.error("  > Tentative d'exécution d'une requête Neo4j sans driver initialisé.")
            raise Exception("Neo4j driver is not initialized.")

        max_retries = 3
        delay = 2  # secondes
        for attempt in range(max_retries):
            try:
                if self.driver:
                    async with self.driver.session() as session:
                        return await query_func(session, *args, **kwargs)
            except (ServiceUnavailable, TransientError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"  > ⚠️ Connexion Neo4j instable ({e}). Tentative {attempt + 2}/{max_retries} dans {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= 2  # Backoff exponentiel
                else:
                    logger.error(f"  > ❌ Échec final de la connexion Neo4j après {max_retries} tentatives.")
                    raise e

    async def purge_database(self) -> bool:
        """Purge la base de données par lots contrôlés."""
        if not self.driver:
            logger.error("Neo4j driver not initialized.")
            return False
        logger.warning("🔥 Processus de purge par lots initialisé...")
        total_deleted = 0
        
        while True:
            try:
                async with self.driver.session() as session:
                    async def purge_batch(tx: Any) -> Any:
                        result = await tx.run("""
                            MATCH (n) WITH n LIMIT 5000
                            DETACH DELETE n RETURN count(n) AS c
                        """)
                        record = await result.single()
                        return dict(record) if record else None
                    
                    summary = await session.execute_write(purge_batch)
                    if not summary or summary['c'] == 0:
                        break
                    total_deleted += summary['c']
                    logger.info(f"  > Lot traité : {summary['c']} nœuds supprimés. (Total: {total_deleted})")
            except Exception as e:
                if "defunct connection" in str(e).lower():
                    logger.warning("  > Connexion perdue, tentative de reconnexion...")
                    await asyncio.sleep(1)
                    continue
                logger.error(f"❌ Erreur durant le traitement d'un lot : {e}")
                raise e
        
        logger.info(f"✅ Processus de purge terminé. Total supprimé: {total_deleted} nœuds.")
        return True
    
    def get_driver(self) -> Any:
        """Get Neo4j driver instance"""
        if not self.driver:
            raise Exception("Neo4j service not initialized")
        return self.driver
    
    async def save_raw_structured_data(self, document_id: str, file_path: str, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sauvegarde les entités et relations initiales (Phase 1) avec re-tentatives."""
        if not self.driver:
            logger.error("Neo4j driver not initialized.")
            return {"entities_created": 0, "relations_created": 0}
        if not entities and not relations:
            return {"entities_created": 0, "relations_created": 0}

        async def transaction_func(session: Any, doc_id: str, fp: str, ents: List[Dict[str, Any]], rels: List[Dict[str, Any]]) -> Any:
            # Créer/mettre à jour le nœud Document
            await session.run("""
                MERGE (d:Document {id: $doc_id})
                SET d.filePath = $file_path, d.lastRawIngested = datetime()
            """, doc_id=doc_id, file_path=fp)

            # Créer les entités avec un label de base :Entity
            for entity in ents:
                await session.run("""
                    MERGE (e:Entity {nom: $nom})
                    ON CREATE SET e.type = $type, e.description = $description
                    WITH e
                    MATCH (d:Document {id: $doc_id})
                    MERGE (e)-[:MENTIONED_IN]->(d)
                """, nom=entity.get('nom'), type=entity.get('type'), description=entity.get('description'), doc_id=doc_id)

            # Créer les relations brutes
            for relation in rels:
                rel_type = relation.get('relation', 'RELATED_TO').replace(' ', '_').upper()
                query = """
                    MATCH (e1:Entity {nom: $entite1})
                    MATCH (e2:Entity {nom: $entite2})
                    CALL apoc.create.relationship(e1, $rel_type, {}, e2) YIELD rel
                    RETURN rel
                """
                await session.run(
                    query,
                    entite1=relation.get('entite1'),
                    entite2=relation.get('entite2'),
                    rel_type=rel_type
                )

        await self._run_with_retry(transaction_func, document_id, file_path, entities, relations)
        return {"entities_created": len(entities), "relations_created": len(relations)}

    async def save_structured_data(self, document_id: str, entities: List[Dict[str, Any]], relations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sauvegarde les entités et relations extraites dans Neo4j"""
        if not self.driver:
            logger.error("Neo4j driver not initialized.")
            return {"entities_created": 0, "relations_created": 0}
        if not entities and not relations:
            logger.info(f"Aucune donnée structurée à sauvegarder pour {document_id}")
            return {"entities_created": 0, "relations_created": 0}
            
        async with self.driver.session() as session:
            try:
                # Créer les entités AVEC LE MARQUAGE TACTIQUE
                for entity in entities:
                    await session.run("""
                        MERGE (e:Entity {nom: $nom, type: $type})
                        SET e.description = $description,
                            e.document_source = $doc_id
                    """,
                    nom=entity.get('nom', ''),
                    type=entity.get('type', 'UNKNOWN'),
                    description=entity.get('description', ''),
                    doc_id=document_id)
                
                # Créer les relations
                for relation in relations:
                    rel_type = relation.get('relation', 'RELATED_TO').replace(' ', '_').upper()
                    # Protection contre l'injection: utiliser une requête paramétrée
                    query = """
                        MATCH (e1:Entity {nom: $entite1})
                        MATCH (e2:Entity {nom: $entite2})
                        CALL apoc.create.relationship(e1, $rel_type, {}, e2) YIELD rel
                        RETURN rel
                    """
                    await session.execute_write(
                        lambda tx: tx.run(
                            query,
                            entite1=relation.get('entite1', ''),
                            entite2=relation.get('entite2', ''),
                            rel_type=rel_type
                        )
                    )
                
                logger.info(f"✅ {len(entities)} entités et {len(relations)} relations sauvegardées pour {document_id}")
                
            except Exception as e:
                logger.error(f"Erreur sauvegarde données structurées: {e}")
                return {"entities_created": 0, "relations_created": 0}
        return {"entities_created": len(entities), "relations_created": len(relations)}

    async def store_chunks(self, document_id: str, file_path: str, chunks: List[str], embeddings: List[List[float]]) -> bool:
        """Stocke les chunks et leurs embeddings pour un document donné avec re-tentatives."""
        if not self.driver:
            logger.error("Neo4j driver not initialized.")
            return False
        
        async def transaction_func(session: Any, doc_id: str, fp: str, chks: List[str], embs: List[List[float]]) -> Any:
            # Assurer l'existence du noeud Document et mettre à jour le file_path
            await session.run("""
                MERGE (d:Document {id: $doc_id})
                ON CREATE SET d.created_at = datetime()
                SET d.filePath = $fp
            """, doc_id=doc_id, fp=fp)
            
            # Transaction pour insérer tous les chunks
            for i, (chunk_text, embedding) in enumerate(zip(chks, embs)):
                chunk_id = f"{doc_id}_chunk_{i}"
                await session.run("""
                    MATCH (d:Document {id: $doc_id})
                    CREATE (c:Chunk {
                        id: $chunk_id,
                        text: $text,
                        embedding: $embedding,
                        chunk_index: $index,
                        char_count: size($text),
                        created_at: datetime(),
                        documentId: $doc_id
                    })-[:BELONGS_TO]->(d)
                """, {
                    "doc_id": doc_id,
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "embedding": embedding,
                    "index": i
                })
            
        await self._run_with_retry(transaction_func, document_id, file_path, chunks, embeddings)
        logger.info(f"N4J: Stocké {len(chunks)} chunks pour le document {document_id}")
        return True

    async def search_chunks_by_vector(self, embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Recherche des chunks similaires et retourne un contexte enrichi."""
        if not self.driver:
            logger.error("Neo4j driver not initialized.")
            return []
        if not embedding:
            return []
        async with self.driver.session() as session:
            result = await session.run("""
                CALL db.index.vector.queryNodes('chunk_embeddings', $limit, $embedding)
                YIELD node, score
                MATCH (node)-[:BELONGS_TO]->(d:Document)
                RETURN
                    node.id AS chunkId,
                    node.text AS text,
                    score,
                    d.id AS documentId,
                    d.filePath AS documentPath
                ORDER BY score DESC
                LIMIT $limit
            """, {"embedding": embedding, "limit": limit})
            records: List[Dict[str, Any]] = []
            async for record in result:
                records.append({
                    "chunkId": record.get("chunkId"),
                    "text": record.get("text"),
                    "score": record.get("score"),
                    "documentId": record.get("documentId"),
                    "documentPath": record.get("documentPath")
                })
            return records

    async def search_chunks_by_fulltext(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recherche des chunks en utilisant l'index full-text."""
        if not self.driver:
            return []

        # Sanitize la query pour Lucene : enlever les caractères spéciaux problématiques
        # et formater pour la recherche full-text
        import re
        # Enlever caractères spéciaux Lucene sauf les espaces
        sanitized = re.sub(r'[^\w\sàéèêôùûïäë-]', '', query, flags=re.UNICODE)
        # Appliquer fuzzy search (~) uniquement sur les mots de 4+ caractères
        words = sanitized.split()
        fulltext_query = ' '.join([f"{word}~" if len(word) >= 4 else word for word in words])

        async with self.driver.session() as session:
            result = await session.run("""
                CALL db.index.fulltext.queryNodes('chunk_text_index', $query)
                YIELD node, score
                MATCH (node)-[:BELONGS_TO]->(d:Document)
                RETURN
                    node.id AS chunkId,
                    node.text AS text,
                    score,
                    d.id AS documentId,
                    d.filePath AS documentPath
                ORDER BY score DESC
                LIMIT $limit
            """, {"query": fulltext_query, "limit": limit})

            records: List[Dict[str, Any]] = []
            async for record in result:
                records.append({
                    "chunkId": record.get("chunkId"),
                    "text": record.get("text"),
                    "score": record.get("score"),
                    "documentId": record.get("documentId"),
                    "documentPath": record.get("documentPath")
                })
            return records

    async def get_relations_from_chunks(self, chunk_ids: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """
        CORRECTIF PROTOCOLE DAN v2 : Récupère les relations des entités en traversant
        correctement le graphe depuis les chunks jusqu'aux documents, puis aux entités.
        """
        if not self.driver or not chunk_ids:
            return []

        # Cette requête suit la piste logique : Chunks -> Document -> Entités -> Relations
        query = """
        // 1. Partir des chunks pertinents identifiés par la recherche vectorielle
        MATCH (chunk:Chunk) WHERE chunk.id IN $chunk_ids

        // 2. Remonter au document parent
        MATCH (chunk)-[:BELONGS_TO]->(doc:Document)

        // 3. Identifier toutes les entités mentionnées dans ce document
        MATCH (entity1:Entity)-[:MENTIONED_IN]->(doc)

        // 4. Explorer les relations de ces entités avec d'autres entités
        MATCH (entity1)-[relation]-(entity2:Entity)
        WHERE entity1 <> entity2

        // 5. Retourner les relations distinctes trouvées
        RETURN DISTINCT
               entity1.nom AS entite,
               type(relation) AS relation,
               entity2.nom AS autre_entite
        LIMIT $limit
        """

        async with self.driver.session() as session:
            result = await session.run(query, {"chunk_ids": chunk_ids, "limit": limit})

            relations: List[Dict[str, Any]] = []
            async for record in result:
                relations.append({
                    "entite": record.get("entite"),
                    "relation": record.get("relation"),
                    "autre_entite": record.get("autre_entite"),
                })
            return relations

    async def get_entity_relations(self, entity_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère toutes les relations d'une entité spécifique."""
        if not self.driver:
            logger.error("Neo4j driver not initialized.")
            return []
        
        try:
            async with self.driver.session() as session:
                # Recherche bidirectionnelle: relations sortantes ET entrantes
                result = await session.run("""
                    MATCH (e:Entity {nom: $entity_name})
                    OPTIONAL MATCH (e)-[r1]->(e2:Entity)
                    OPTIONAL MATCH (e3:Entity)-[r2]->(e)
                    WITH e, 
                         collect(DISTINCT {entite: e.nom, relation: type(r1), autre_entite: e2.nom}) as outgoing,
                         collect(DISTINCT {entite: e3.nom, relation: type(r2), autre_entite: e.nom}) as incoming
                    WITH (outgoing + incoming) as all_rels
                    UNWIND all_rels as rel
                    WITH rel WHERE rel.autre_entite IS NOT NULL
                    RETURN DISTINCT rel.entite as entite, rel.relation as relation, rel.autre_entite as autre_entite
                    LIMIT $limit
                """, {"entity_name": entity_name, "limit": limit})
                
                relations: List[Dict[str, Any]] = []
                async for record in result:
                    relations.append({
                        "entite": record.get("entite"),
                        "relation": record.get("relation"),
                        "autre_entite": record.get("autre_entite"),
                    })
                return relations
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des relations de l'entité {entity_name}: {e}")
            return []

    async def find_paths_between_entities(self, entity_names: List[str], max_depth: int = 3) -> List[str]:
        """
        Trouve et formate les chemins les plus courts entre une liste d'entités dans le graphe.
        """
        if not self.driver or len(entity_names) < 2:
            return []

        # On prend les 5 entités les plus pertinentes pour éviter des requêtes trop complexes
        entity_names = entity_names[:5]

        # Requête alternative sans APOC si non disponible
        query_no_apoc = f"""
        MATCH (e1:Entity), (e2:Entity)
        WHERE e1.nom IN $names AND e2.nom IN $names AND elementId(e1) < elementId(e2)
        MATCH p = allShortestPaths((e1)-[*1..{max_depth}]-(e2))
        RETURN p
        LIMIT 20
        """

        context_lines = []
        try:
            async with self.driver.session() as session:
                result = await session.run(query_no_apoc, names=entity_names)
                
                paths = [record["p"] async for record in result]
                
                for path in paths:
                    # Un chemin est une séquence alternée de nœuds et de relations.
                    # Itérer sur les relations pour reconstruire le chemin de manière fiable.
                    line_parts = []
                    for rel in path.relationships:
                        start_node = rel.start_node
                        end_node = rel.end_node
                        
                        start_name = start_node.get('nom', 'Entité Inconnue')
                        end_name = end_node.get('nom', 'Entité Inconnue')
                        rel_type = rel.type
                        
                        line_parts.append(f"'{start_name}' --[{rel_type}]--> '{end_name}'")
                    
                    if line_parts:
                        context_lines.append(f"- Chemin trouvé : {' '.join(line_parts)}")

                return list(dict.fromkeys(context_lines))
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de chemins Neo4j : {e}")
            return []

    async def get_statistics(self) -> Dict[str, int]:
        """Récupère les statistiques de la base Neo4j."""
        if not self.driver:
            logger.error("Neo4j driver not initialized.")
            return {"nodes": 0, "chunks": 0, "documents": 0, "relations": 0}
        
        try:
            async with self.driver.session() as session:
                # Compter tous les nœuds
                result = await session.run("MATCH (n) RETURN count(n) as count")
                record = await result.single()
                nodes_count = record["count"] if record else 0
                
                # Compter les chunks
                result = await session.run("MATCH (c:Chunk) RETURN count(c) as count")
                record = await result.single()
                chunks_count = record["count"] if record else 0
                
                # Compter les documents
                result = await session.run("MATCH (d:Document) RETURN count(d) as count")
                record = await result.single()
                docs_count = record["count"] if record else 0
                
                # Compter toutes les relations
                result = await session.run("MATCH ()-[r]->() RETURN count(r) as count")
                record = await result.single()
                relations_count = record["count"] if record else 0
                
                return {
                    "nodes": nodes_count,
                    "chunks": chunks_count,
                    "documents": docs_count,
                    "relations": relations_count
                }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {"nodes": 0, "chunks": 0, "documents": 0, "relations": 0}

    async def get_indexed_documents(self) -> List[Dict[str, Any]]:
        """Get all documents that are actually indexed in Neo4j with their details"""
        if not self.driver:
            logger.error("Neo4j driver not initialized.")
            return []

        try:
            async with self.driver.session() as session:
                # Get all Document nodes with related chunk and entity counts
                result = await session.run("""
                    MATCH (d:Document)
                    OPTIONAL MATCH (d)<-[:BELONGS_TO]-(c:Chunk)
                    OPTIONAL MATCH (d)<-[:FROM_DOCUMENT]-(e:Entity)
                    RETURN d.id as document_id, 
                           d.file_path as file_path,
                           d.created_at as created_at,
                           count(DISTINCT c) as chunk_count,
                           count(DISTINCT e) as entity_count
                    ORDER BY d.created_at DESC
                """)
                
                documents = []
                async for record in result:
                    documents.append({
                        "document_id": record["document_id"],
                        "file_path": record["file_path"],
                        "created_at": record["created_at"],
                        "chunk_count": record["chunk_count"],
                        "entity_count": record["entity_count"]
                    })
                
                return documents
        except Exception as e:
            logger.error(f"Error retrieving indexed documents: {e}")
            return []

    async def get_knowledge_graph(self, limit: int = 300) -> Dict[str, Any]:
        """Retrieve knowledge graph data for visualization

        Args:
            limit: Maximum number of entities to retrieve (default: 300)

        Returns:
            Dictionary with nodes and edges for graph visualization
        """
        if not self.driver:
            logger.error("Neo4j driver not initialized.")
            return {"nodes": [], "edges": [], "statistics": {}}

        try:
            async with self.driver.session() as session:
                # Get all entity nodes (excluding Chunk and Document nodes for cleaner visualization)
                # Filter only nodes with minimum 1 connection for better readability
                entities_result = await session.run("""
                    MATCH (e)
                    WHERE NOT e:Chunk AND NOT e:Document
                    WITH e, labels(e) as nodeLabels,
                         count{(e)-[]->()} + count{(e)<-[]-()} as degree
                    WHERE degree >= 1
                    RETURN
                        id(e) as id,
                        e.nom as name,
                        e.type as type,
                        nodeLabels[0] as label,
                        degree
                    ORDER BY degree DESC
                    LIMIT $limit
                """, limit=limit)

                nodes = []
                node_ids = []

                async for record in entities_result:
                    node_id = str(record["id"])
                    node_ids.append(node_id)

                    # Assign colors based on node type
                    type_colors = {
                        "PERSON": "#3B82F6",      # Blue
                        "ORGANIZATION": "#10B981", # Green
                        "LOCATION": "#F59E0B",     # Orange
                        "CONTRACT": "#8B5CF6",     # Purple
                        "LEGAL_ARTICLE": "#EF4444",# Red
                        "DATE": "#EC4899",         # Pink
                    }

                    node_type = record["label"] or "ENTITY"
                    color = type_colors.get(node_type, "#6B7280")  # Default gray

                    # Size based on number of connections (degree)
                    degree = record["degree"] or 0
                    size = min(8 + degree * 1.5, 25)  # Scale between 8 and 25 (plus petit)

                    nodes.append({
                        "id": node_id,
                        "label": record["name"] or f"{node_type}_{node_id}",
                        "type": node_type,
                        "size": size,
                        "color": color,
                        "degree": degree
                    })

                # Get relationships between these entities
                edges = []
                if node_ids:
                    relations_result = await session.run("""
                        MATCH (source)-[r]->(target)
                        WHERE id(source) IN $nodeIds AND id(target) IN $nodeIds
                        RETURN
                            id(source) as source_id,
                            id(target) as target_id,
                            type(r) as rel_type,
                            id(r) as rel_id
                    """, nodeIds=[int(nid) for nid in node_ids])

                    async for record in relations_result:
                        edges.append({
                            "id": str(record["rel_id"]),
                            "source": str(record["source_id"]),
                            "target": str(record["target_id"]),
                            "type": record["rel_type"],
                            "weight": 1
                        })

                # Get statistics
                stats = await self.get_statistics()

                return {
                    "nodes": nodes,
                    "edges": edges,
                    "statistics": stats
                }

        except Exception as e:
            logger.error(f"Error retrieving knowledge graph: {e}")
            return {"nodes": [], "edges": [], "statistics": {}}

    async def close(self) -> None:
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")

# Global Neo4j service instance
neo4j_service = None

def get_neo4j_service() -> Neo4jService:
    """Dependency function for FastAPI"""
    global neo4j_service
    if neo4j_service is None:
        neo4j_service = Neo4jService()
    return neo4j_service