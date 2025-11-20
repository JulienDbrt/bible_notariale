import os
import re
import uuid
import logging
import json
import asyncio
import tiktoken
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import openai

# --- Imports internes ---
# Ces services sont les composants principaux du système.
from .neo4j_service import Neo4jService, get_neo4j_service
from .minio_service import MinioService, get_minio_service

logger = logging.getLogger(__name__)

# ========================================================================
# Stratégies RAG
# ========================================================================
class RAGStrategy(Enum):
    """Stratégies de recherche pour le Query Planner."""
    VECTOR_ONLY = "VECTOR_ONLY"  # Questions conceptuelles ouvertes
    GRAPH_FIRST = "GRAPH_FIRST"  # Questions relationnelles directes
    HYBRID = "HYBRID"  # Questions complexes (défaut)

class RAGService:
    """
    Service RAG unifié avec architecture cognitive avancée.
    """
    
    def __init__(self, neo4j_service: Neo4jService, minio_service: MinioService):
        self.neo4j = neo4j_service
        self.minio = minio_service
        
        # Client OpenAI pour embeddings (API OpenAI directe)
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("⚠️ La variable d'environnement OPENAI_API_KEY est manquante.")
        self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key, timeout=180.0)

        # Configuration granulaire des clients LLM selon l'endpoint spécifié
        # Client pour LLM Extraction
        extraction_endpoint_type = os.getenv("LLM_EXTRACTION_ENDPOINT", "openai").lower()
        if extraction_endpoint_type == "openrouter":
            extraction_api_key = os.getenv("OR_API_KEY")
            extraction_base_url = os.getenv("OR_ENDPOINT", "https://openrouter.ai/api/v1")
            if not extraction_api_key:
                raise ValueError("⚠️ OR_API_KEY est manquante pour LLM_EXTRACTION_ENDPOINT=openrouter")
        else:  # openai
            extraction_api_key = openai_api_key
            extraction_base_url = "https://api.openai.com/v1"
        self.extraction_client = openai.AsyncOpenAI(api_key=extraction_api_key, base_url=extraction_base_url, timeout=180.0)

        # Client pour LLM Planner
        planner_endpoint_type = os.getenv("LLM_PLANNER_ENDPOINT", "openai").lower()
        if planner_endpoint_type == "openrouter":
            planner_api_key = os.getenv("OR_API_KEY")
            planner_base_url = os.getenv("OR_ENDPOINT", "https://openrouter.ai/api/v1")
            if not planner_api_key:
                raise ValueError("⚠️ OR_API_KEY est manquante pour LLM_PLANNER_ENDPOINT=openrouter")
        else:  # openai
            planner_api_key = openai_api_key
            planner_base_url = "https://api.openai.com/v1"
        self.planner_client = openai.AsyncOpenAI(api_key=planner_api_key, base_url=planner_base_url, timeout=180.0)

        # Client pour LLM Synthesis
        synthesis_endpoint_type = os.getenv("LLM_SYNTHESIS_ENDPOINT", "openai").lower()
        if synthesis_endpoint_type == "openrouter":
            synthesis_api_key = os.getenv("OR_API_KEY")
            synthesis_base_url = os.getenv("OR_ENDPOINT", "https://openrouter.ai/api/v1")
            if not synthesis_api_key:
                raise ValueError("⚠️ OR_API_KEY est manquante pour LLM_SYNTHESIS_ENDPOINT=openrouter")
        else:  # openai
            synthesis_api_key = openai_api_key
            synthesis_base_url = "https://api.openai.com/v1"
        self.synthesis_client = openai.AsyncOpenAI(api_key=synthesis_api_key, base_url=synthesis_base_url, timeout=180.0)

    # ========================================================================
    # SECTION 1 : OUTILS DE DÉCOUPAGE (CHUNKING)
    # ========================================================================

    def _split_text_into_large_chunks(self, text: str, max_tokens: int) -> List[str]:
        """Découpage optimisé pour l'analyse sémantique."""
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
        except KeyError:
            encoding = tiktoken.encoding_for_model("gpt-4")
        tokens = encoding.encode(text)
        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i + max_tokens]
            chunks.append(encoding.decode(chunk_tokens))
        return chunks

    def _chunk_text_for_retrieval(self, text: str, chunk_size_tokens: Optional[int] = None, overlap_tokens: Optional[int] = None) -> List[str]:
        """
        Découpage adaptatif pour la recherche vectorielle.
        Méthode : Agrégation Sémantique Contrôlée.
        """
        # Utiliser les valeurs par défaut depuis les variables d'environnement
        chunk_size = chunk_size_tokens if chunk_size_tokens is not None else int(os.getenv("RETRIEVAL_CHUNK_SIZE_TOKENS", "512"))
        if overlap_tokens is None:
            overlap = int(os.getenv("RETRIEVAL_OVERLAP_TOKENS", "50"))
        else:
            overlap = overlap_tokens
            
        if not text or not isinstance(text, str):
            return []

        try:
            encoding = tiktoken.get_encoding("cl100k_base")
        except KeyError:
            encoding = tiktoken.encoding_for_model("gpt-4")

        final_chunks = []
        
        # 1. Respect des paragraphes comme frontières sémantiques principales.
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # 2. Segmentation par phrases à l'intérieur de chaque paragraphe.
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            
            if not sentences:
                continue

            # Tokenize toutes les phrases du paragraphe
            sentence_tokens = [encoding.encode(s) for s in sentences]

            current_chunk_tokens: list[int] = []
            for i, tokens in enumerate(sentence_tokens):
                # 3. Agrégation de phrases jusqu'à atteindre la taille de chunk cible.
                if len(current_chunk_tokens) + len(tokens) > chunk_size and current_chunk_tokens:
                    # Finaliser le chunk actuel
                    final_chunks.append(encoding.decode(current_chunk_tokens))
                    
                    # 4. Créer le chevauchement en tokens
                    # On conserve une partie de la fin du chunk précédent
                    overlap_start_index = max(0, len(current_chunk_tokens) - overlap)
                    current_chunk_tokens = current_chunk_tokens[overlap_start_index:]

                current_chunk_tokens.extend(tokens)
            
            # Ajouter le dernier chunk restant du paragraphe
            if current_chunk_tokens:
                final_chunks.append(encoding.decode(current_chunk_tokens))

        return final_chunks

    # ========================================================================
    # SECTION 2 : OUTILS COGNITIFS (LLM & EMBEDDING)
    # ========================================================================

    async def _get_embeddings(self, chunks: List[str]) -> Optional[List[List[float]]]:
        """Génération d'embeddings avec logistique adaptative."""
        if not chunks: return []
        embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        TOKEN_LIMIT_PER_CHUNK = int(os.getenv("EMBEDDING_TOKEN_LIMIT_PER_CHUNK", "8190"))
        BATCH_TOKEN_LIMIT = int(os.getenv("EMBEDDING_BATCH_TOKEN_LIMIT", "250000"))
        try:
            encoding = tiktoken.encoding_for_model(embedding_model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        
        tokenized_chunks = []
        for i, chunk in enumerate(chunks):
            tokens = encoding.encode(chunk)
            if len(tokens) > TOKEN_LIMIT_PER_CHUNK:
                logger.warning(f"Chunk {i} trop large ({len(tokens)}t). Troncature.")
                tokenized_chunks.append(tokens[:TOKEN_LIMIT_PER_CHUNK])
            else:
                tokenized_chunks.append(tokens)
        
        if not tokenized_chunks: return None
        all_embeddings: list[list[float]] = []
        current_batch_chunks: list[list[int]] = []
        current_batch_tokens_count = 0
        
        for tokens in tokenized_chunks:
            if current_batch_tokens_count + len(tokens) > BATCH_TOKEN_LIMIT:
                if not await self._process_embedding_batch(embedding_model, encoding, current_batch_chunks, all_embeddings): return None
                current_batch_chunks, current_batch_tokens_count = [], 0
            current_batch_chunks.append(tokens)
            current_batch_tokens_count += len(tokens)
        
        if current_batch_chunks:
            if not await self._process_embedding_batch(embedding_model, encoding, current_batch_chunks, all_embeddings): return None
            
        return all_embeddings

    async def _process_embedding_batch(self, model: Any, encoding: Any, batch_tokens: Any, all_embeddings: Any) -> bool:
        """Sous-routine pour traiter un batch d'embedding."""
        try:
            logger.info(f"  > Embedding batch de {len(batch_tokens)} chunks...")

            # Récupérer les dimensions depuis les variables d'environnement
            embedding_dimensions = os.getenv("EMBEDDING_DIMENSIONS")

            # Construire les paramètres de l'API
            api_params = {
                "model": model,
                "input": [encoding.decode(t) for t in batch_tokens]
            }

            # Ajouter le paramètre dimensions seulement si spécifié
            # (pour réduire les dimensions des modèles text-embedding-3-*)
            if embedding_dimensions:
                api_params["dimensions"] = int(embedding_dimensions)

            response = await self.openai_client.embeddings.create(**api_params)
            all_embeddings.extend([item.embedding for item in response.data])
            return True
        except Exception as e:
            logger.error(f"  > ❌ Échec sur un batch d'embedding. Abandon. Erreur: {e}")
            return False

    async def _extract_entities_from_text(self, text_chunk: str) -> Dict[str, List[Any]]:
        """Extraction sémantique robuste via LLM."""
        prompt = f"""
        Tu es un expert en modélisation de connaissance pour le domaine notarial français. Analyse ce texte et extrais TOUTES les entités et relations pertinentes.

        **DIRECTIVE 1 : EXTRACTION D'ENTITÉS DIVERSIFIÉES**
        Identifie les entités suivantes avec la plus grande précision :
        - **Personne**: Noms propres d'individus (ex: "Me Romain Lecordier", "Eric Dupond-Moretti").
        - **Organisation**: Noms d'entreprises, d'études notariales, d'institutions (ex: "MMA IARD", "Conseil Supérieur du Notariat", "Chambre des Notaires").
        - **ConceptJuridique**: Termes techniques, doctrines, procédures, types de contrats ou d'actes (ex: "franchise aggravée", "société multi-offices (SMO)", "comparution à distance", "partage amiable", "apostille", "droit de présentation", "mandat non-exclusif", "VEFA"). Sois très agressif sur ce type.
        - **Document**: Références à des documents spécifiques (ex: "contrat n° 145 154 406", "décret 2024-906", "avenant n°61").
        - **Date**: Dates précises mentionnées (ex: "1er janvier 2025", "24 avril 2023").
        - **Lieu**: Villes, régions, adresses (ex: "Basse-Normandie", "Caen").

        **DIRECTIVE 2 : EXTRACTION DE RELATIONS EXHAUSTIVE**
        Force-toi à lier les entités entre elles. Il vaut mieux une relation potentielle qu'aucune relation. Cherche activement les relations de type :
        - **EST_UN_TYPE_DE** (ex: "franchise aggravée" EST_UN_TYPE_DE "franchise")
        - **S_APPLIQUE_A** (ex: "décret 2024-906" S_APPLIQUE_A "inspection périodique")
        - **A_POUR_REGLE** (ex: "contrat cyber" A_POUR_REGLE "mot de passe de 12 caractères")
        - **MEMBRE_DE**, **PARTIE_DE** (ex: "Me Romain Lecordier" MEMBRE_DE "Chambre des Notaires")
        - **SITUÉ_À** (ex: "Office notarial" SITUÉ_À "Caen")
        - **A_POUR_DATE_DEFFET** (ex: "Avenant n°61" A_POUR_DATE_DEFFET "1er mai 2025")
        
        **FORMAT DE SORTIE STRICT :**
        Réponds UNIQUEMENT en JSON VALIDE avec la structure suivante : {{"entities": [{{"nom": "Nom Entité", "type": "TYPE_ENTITE", "description": "courte description"}}], "relations": [{{"entite1": "Nom1", "relation": "TYPE_RELATION", "entite2": "Nom2"}}]}}.
        Les types d'entités doivent être exactement : `Personne`, `Organisation`, `ConceptJuridique`, `Document`, `Date`, `Lieu`.
        Si le texte est vide ou incohérent, retourne : {{"entities": [], "relations": []}}.
        NE PRODUIS AUCUN TEXTE EN DEHORS DE L'OBJET JSON.

        Texte à analyser: --- {text_chunk} ---
        """
        content = None
        try:
            # MODIFICATION : Appel via extraction_client (OpenRouter ou OpenAI selon config)
            response = await self.extraction_client.chat.completions.create(
                model=os.getenv("LLM_EXTRACTION_MODEL", "gpt-4.1-mini-2025-04-14"),
                messages=[{"role": "user", "content": prompt}],
                temperature=float(os.getenv("LLM_EXTRACTION_TEMPERATURE", "0.0")),
                response_format={"type": "json_object"},
                max_tokens=int(os.getenv("LLM_EXTRACTION_MAX_TOKENS", "8096"))
            )
            content = response.choices[0].message.content
            if not content: return {"entities": [], "relations": []}
            result = json.loads(content)
            return {"entities": result.get("entities", []), "relations": result.get("relations", [])}
        except json.JSONDecodeError as json_err:
            logger.warning(f"  > ⚠️  Échec du parsing JSON. Tentative de réparation... Erreur: {json_err}")
            
            # Processus de réparation JSON
            if content:
                repaired_json = await self._repair_json_with_llm(content)
                if repaired_json:
                    logger.info("  > ✅ JSON réparé avec succès.")
                    return repaired_json
            
            logger.error(f"  > ❌ Échec de la réparation JSON. Contenu LLM fautif : {content or 'None'}")
            return {"entities": [], "relations": []}
        except Exception as e:
            logger.error(f"Erreur d'extraction d'entités: {e}")
            return {"entities": [], "relations": []}

    async def _repair_json_with_llm(self, broken_json_string: str) -> Optional[Dict[str, Any]]:
        """Utilise un LLM pour tenter de réparer un JSON malformé."""
        prompt = f"""
        Le JSON suivant est malformé. Corrige-le pour qu'il soit syntaxiquement valide.
        Ne modifie QUE la syntaxe. Ne change pas les données. Ne rajoute rien.
        Ne réponds QUE avec l'objet JSON corrigé. Pas de texte avant ou après.

        JSON à réparer :
        ---
        {broken_json_string}
        ---
        """
        try:
            response = await self.openai_client.chat.completions.create(
                model=os.getenv("LLM_PLANNER_MODEL", "gpt-4.1-nano-2025-04-14"),
                messages=[{"role": "user", "content": prompt}],
                temperature=float(os.getenv("LLM_PLANNER_TEMPERATURE", "0.0")),
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            if not content:
                return None
            result = json.loads(content)
            return result if isinstance(result, dict) else None
        except Exception as e:
            logger.error(f"  > ❌ La tentative de réparation JSON a échoué : {e}")
            return None

    # ========================================================================
    # SECTION 3 : PHASE 1 - INGESTION INITIALE
    # ========================================================================

    async def ingest_raw_document(self, document_id: str, file_path: str, text_content: str) -> bool:
        """Phase 1 : Ingestion et extraction sémantique initiale."""
        logger.info(f"🔬 Phase 1: Analyse initiale de {document_id}")
        try:
            # 1. Analyse sémantique
            max_tokens = int(os.getenv("ANALYSIS_CHUNK_SIZE_TOKENS", "60000"))
            analysis_chunks = self._split_text_into_large_chunks(text_content, max_tokens)
            all_entities, all_relations = [], []
            for chunk in analysis_chunks:
                data = await self._extract_entities_from_text(chunk)
                if data.get('entities'): all_entities.extend(data['entities'])
                if data.get('relations'): all_relations.extend(data['relations'])
            
            # 2. Sauvegarde des données brutes
            await self.neo4j.save_raw_structured_data(document_id, file_path, all_entities, all_relations)

            # 3. Préparation pour la recherche vectorielle
            vector_chunks = self._chunk_text_for_retrieval(text_content)
            embeddings = await self._get_embeddings(vector_chunks)
            if embeddings is None: raise RuntimeError("Échec de la génération des embeddings.")
            
            # 4. Stockage des vecteurs avec le chemin du fichier
            await self.neo4j.store_chunks(document_id, file_path, vector_chunks, embeddings)
            return True
        except Exception as e:
            logger.error(f"❌ Échec de la Phase 1 pour {document_id}: {e}", exc_info=True)
            return False

    # ========================================================================
    # SECTION 4 : PLANIFICATEUR DE REQUÊTES (QUERY PLANNER)
    # ========================================================================
    
    async def _llm_query_planner(self, question: str) -> Optional[RAGStrategy]:
        """
        Classifieur d'intention basé sur LLM.
        Rapide, précis, efficace.
        """
        prompt = f"""
        Tu es un planificateur de requêtes expert pour un système RAG notarial.
        Analyse la question de l'utilisateur et détermine la meilleure stratégie de recherche parmi les options suivantes :

        - "VECTOR_ONLY": Pour les questions générales, conceptuelles ou de définition qui ne nomment pas d'entités spécifiques.
          Exemples: "Expliquez la franchise aggravée.", "Qu'est-ce qu'une SMO ?"

        - "GRAPH_FIRST": Pour les questions qui cherchent des relations directes entre des entités spécifiques et nommées.
          Exemples: "Quel est le lien entre la société MMA IARD et le contrat Cyber ?", "Qui est le notaire de l'époux survivant en Basse-Normandie ?"

        - "HYBRID": Pour les questions complexes, les scénarios pratiques ou les questions qui mélangent des concepts généraux avec des entités spécifiques. C'est la stratégie par défaut.
          Exemples: "Un office de 15 salariés peut-il ne pas verser le 13ème mois ?", "Quelle est la procédure si un cohéritier ne répond pas ?"

        Réponds UNIQUEMENT avec un objet JSON valide contenant la clé "strategy" et la valeur correspondante.
        Exemple de réponse : {{"strategy": "HYBRID"}}
        NE PRODUIS AUCUN TEXTE EN DEHORS DE L'OBJET JSON.

        Question à analyser: --- {question} ---
        """
        try:
            # MODIFICATION : Appel direct au client OpenAI, modèle rapide
            response = await self.openai_client.chat.completions.create(
                model=os.getenv("LLM_PLANNER_MODEL", "gpt-4.1-nano-2025-04-14"), # Modèle pour la planification
                messages=[{"role": "user", "content": prompt}],
                temperature=float(os.getenv("LLM_PLANNER_TEMPERATURE", "0.0")),
                response_format={"type": "json_object"},
                max_tokens=50
            )
            content = response.choices[0].message.content
            if not content:
                return None
            
            data = json.loads(content)
            strategy_str = data.get("strategy")
            
            # Valider que la stratégie est légitime
            if strategy_str in RAGStrategy._value2member_map_:
                return RAGStrategy(strategy_str)
            else:
                logger.warning(f"  > Le planificateur LLM a retourné une stratégie invalide : {strategy_str}")
                return None
                
        except Exception as e:
            logger.error(f"  > ❌ Erreur du planificateur LLM : {e}")
            return None  # Échec -> le fallback sera utilisé

    async def _select_rag_strategy(self, question: str) -> RAGStrategy:
        """
        VERSION MISE À NIVEAU : Orchestre le choix de la stratégie.
        Priorité au planificateur LLM, fallback sur le système de secours (regex).
        """
        # 1. Tentative avec le planificateur intelligent
        llm_strategy = await self._llm_query_planner(question)
        if llm_strategy:
            logger.info(f"  > Stratégie sélectionnée par LLM : {llm_strategy.value}")
            return llm_strategy
            
        # 2. En cas d'échec, activation du système de fallback
        logger.warning("  > Échec du planificateur LLM. Bascule vers le système de fallback (heuristiques regex).")
        question_lower = question.lower()
        
        if re.search(r'\b(qui|quel est le lien|relation entre|associé|rattaché|connecté)\b', question_lower) and len(re.findall(r'[A-Z][a-z]+', question)) > 1:
            logger.info("  > Stratégie de secours sélectionnée : GRAPH_FIRST")
            return RAGStrategy.GRAPH_FIRST

        if re.search(r'\b(explique|comment|pourquoi|quel est le principe|définition|qu\'est-ce que)\b', question_lower) and len(re.findall(r'[A-Z][a-z]+', question)) < 2:
            logger.info("  > Stratégie de secours sélectionnée : VECTOR_ONLY")
            return RAGStrategy.VECTOR_ONLY
            
        logger.info("  > Stratégie de secours sélectionnée : HYBRID")
        return RAGStrategy.HYBRID

    # ========================================================================
    # SECTION 5 : STRATÉGIES DE RECHERCHE SPÉCIALISÉES
    # ========================================================================

    async def _execute_vector_only(self, question: str) -> str:
        """Exécute une recherche vectorielle pure."""
        logger.info("  > Exécution VECTOR_ONLY : Recherche conceptuelle pure")
        question_embedding_list = await self._get_embeddings([question])
        if not question_embedding_list: return ""
        question_embedding = question_embedding_list[0]
        
        chunks = await self.neo4j.search_chunks_by_vector(question_embedding, limit=10)
        if not chunks: return ""
        
        context_parts = ["Contexte extrait des documents pertinents:"]
        context_parts.extend([f"- {c['text']}" for c in chunks])
        return "\n".join(context_parts)

    async def _execute_graph_first(self, question: str) -> str:
        """
        Exécute une recherche priorisant le graphe.
        Séquence : Question -> Extraction d'entités -> Recherche de chemins dans Neo4j -> Contexte.
        """
        logger.info("  > Exécution de la stratégie GRAPH_FIRST...")
        
        # 1. Identifier les entités
        entities = await self._extract_entities_from_query(question)
        if not entities or len(entities) < 2:
            logger.warning("  > Moins de 2 entités trouvées, GRAPH_FIRST inefficace. Fallback sur HYBRID.")
            return await self._execute_hybrid(question)
        
        logger.info(f"  > Entités identifiées dans la requête : {entities}")
        
        # 2. Rechercher les connexions dans le graphe
        paths_context = await self.neo4j.find_paths_between_entities(entities, max_depth=3)
        
        if not paths_context:
            logger.warning("  > Aucun chemin trouvé entre les entités. Fallback sur HYBRID.")
            return await self._execute_hybrid(question)
            
        logger.info(f"  > {len(paths_context)} éléments de contexte trouvés via le graphe.")
        
        # 3. Construire le contexte final
        context = "Informations extraites du graphe de connaissances basé sur les entités de la question:\n"
        context += "\n".join(paths_context)
        
        return context

    async def _execute_hybrid(self, question: str) -> str:
        """Exécute la stratégie hybride standard (Vecteur -> Graphe)."""
        logger.info("  > Exécution HYBRID : Approche combinée")
        question_embedding_list = await self._get_embeddings([question])
        if not question_embedding_list: return ""
        question_embedding = question_embedding_list[0]
        
        retrieved_chunks = await self.neo4j.search_chunks_by_vector(question_embedding, limit=5)
        if not retrieved_chunks: return ""

        context_parts = ["Contexte extrait des documents pertinents:"]
        context_parts.extend([f"- {c['text']}" for c in retrieved_chunks])
        
        # Enrichissement par le graphe
        chunk_ids = [r['chunkId'] for r in retrieved_chunks]
        relations = await self.neo4j.get_relations_from_chunks(chunk_ids, limit=10)
        
        if relations:
            context_parts.append("\nInformations contextuelles du graphe de connaissances:")
            for rel in relations:
                context_parts.append(f"- L'entité '{rel['entite']}' a une relation '{rel['relation']}' avec '{rel['autre_entite']}'.")
        
        return "\n".join(context_parts)

    async def _extract_entities_from_query(self, question: str) -> List[str]:
        """
        Extraction d'entités plus agressive et robuste.
        """
        prompt = f"""
        Ta mission est d'extraire les entités nommées CLÉS d'une question. Sois agressif.
        Cible : Personnes, Organisations, Concepts Juridiques spécifiques, Documents.
        
        RÈGLES :
        1. Ne retourne QUE du JSON.
        2. Le JSON doit être une liste de chaînes de caractères.
        3. Si tu ne trouves rien, retourne une liste vide [].

        Exemples :
        - "Quel est le contrat entre MMA IARD et le CSN ?" -> ["MMA IARD", "CSN", "contrat"]
        - "Comment fonctionne la franchise aggravée ?" -> ["franchise aggravée"]
        
        Question: --- {question} ---
        """
        content = None
        try:
            # Utilisation d'un modèle rapide et peu coûteux pour cette tâche ciblée
            response = await self.extraction_client.chat.completions.create(
                model=os.getenv("LLM_EXTRACTION_MODEL", "gpt-4.1-mini-2025-04-14"), # Un modèle rapide est suffisant
                messages=[{"role": "user", "content": prompt}],
                temperature=float(os.getenv("LLM_EXTRACTION_TEMPERATURE", "0.0")),
                response_format={"type": "json_object"},
                max_tokens=856
            )
            content = response.choices[0].message.content
            if not content:
                return []
            
            data = json.loads(content)
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                # Cherche une clé qui contient une liste
                for key, value in data.items():
                    if isinstance(value, list):
                        return value
            return [] # Si le format est inattendu, on retourne une liste vide

        except json.JSONDecodeError:
            logger.warning(f"  > Le LLM a retourné un JSON invalide pour l'extraction d'entités de la requête. Tentative de réparation.")
            if content:
                repaired_json = await self._repair_json_with_llm(content)
                if repaired_json and isinstance(repaired_json, list):
                        return repaired_json
            logger.error(f"  > Échec de la réparation du JSON. Contenu fautif: {content or 'None'}")
            return [] # Retourner une liste vide en cas d'échec final.
        except Exception as e:
            logger.error(f"Erreur d'extraction d'entités de la requête: {e}")
            return []

    async def _synthesize_answer(self, question: str, context: str) -> str:
        """Génère la réponse finale à partir du contexte consolidé."""
        prompt = f"""
        Tu es un assistant notarial expert. En te basant EXCLUSIVEMENT sur le contexte fourni, réponds à la question.
        Sois factuel, concis et précis. Si l'information n'est pas dans le contexte, dis-le clairement.

        CONTEXTE:
        ---
        {context}
        ---

        QUESTION: {question}
        
        RÉPONSE:
        """
        
        # MODIFICATION : Appel via synthesis_client (OpenAI API selon config)
        response = await self.synthesis_client.chat.completions.create(
            model=os.getenv("LLM_SYNTHESIS_MODEL", "gpt-4.1-2025-04-14"), # Modèle pour la synthèse
            messages=[{"role": "user", "content": prompt}],
            temperature=float(os.getenv("LLM_SYNTHESIS_TEMPERATURE", "0.3")),
            max_tokens=2024
        )
        
        return response.choices[0].message.content or "Le modèle n'a pas fourni de réponse."

    async def _synthesize_answer_with_citations(self, question: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère la réponse finale avec nuance, citations, et gestion de l'incertitude.
        PROTOCOLE DAN v5.1.
        """
        # --- Gestion de l'échec de récupération ---
        if not context_chunks:
            logger.warning("  > Synthèse démarrée sans contexte. Réponse d'incertitude.")
            answer = "Je n'ai pas trouvé d'information précise concernant votre question dans les documents disponibles. Pourriez-vous reformuler votre demande, peut-être en utilisant d'autres termes ?"
            return {"answer": answer, "citations": []}

        # --- Création du contexte pour le LLM ---
        context_for_llm = []
        for i, chunk in enumerate(context_chunks):
            doc_path = chunk.get('documentPath', 'Source inconnue')
            context_for_llm.append(f"[Passage {i+1} - Document: {doc_path}]\n{chunk['text']}")
        context_str = "\n\n".join(context_for_llm)

        # --- NOUVEAU PROMPT DE SYNTHÈSE NUANCÉE ---
        prompt = f"""
        Tu es un assistant notarial expert, prudent et précis. Ta mission est de répondre à la question de l'utilisateur en te basant EXCLUSIVEMENT sur les passages de documents fournis ci-dessous.

        **DIRECTIVES DE COMPORTEMENT :**

        1.  **Réponse Basée sur les Passages :** Si le contexte contient une réponse claire et directe, fournis-la de manière factuelle et concise. Cite les passages APRÈS chaque information que tu donnes, en utilisant le format : "Information. [Passage X]".

        2.  **Gestion de l'Incertitude (Réponse Partielle) :** Si le contexte contient des informations connexes mais pas la réponse exacte, ne dis PAS "l'information n'est pas disponible". Au lieu de ça :
            - Fournis les informations pertinentes que tu as trouvées.
            - Souligne explicitement ce qui manque pour répondre complètement.
            - Invite l'utilisateur à préciser sa question.
            - Exemple : "Les documents mentionnent les franchises générales pour la fraude informatique [Passage 2], mais ne spécifient pas le cas de l'option 8 du contrat ITT. Pourriez-vous préciser le type de contrat ou l'assureur concerné ?"

        3.  **Gestion de l'Absence d'Information :** Si le contexte est totalement hors-sujet et ne permet AUCUN début de réponse, alors seulement, utilise une formule nuancée :
            - "Je n'ai pas trouvé d'information précise concernant votre question dans les documents consultés. Serait-il possible de la reformuler ou d'apporter plus de détails ?"

        4.  **Gestion des Questions Déontologiques ou Limites (Malicious Attempts) :** Si la question semble inappropriée, cherche à contourner une règle déontologique, ou demande une information manifestement inexistante (ex: "procédure pour déclarer un vol de cryptomonnaies"), ne réponds pas directement. Adopte une posture professionnelle :
            - Rappelle le principe général ou la règle applicable (si disponible dans le contexte).
            - Explique pourquoi la question est complexe ou ne peut être répondue telle quelle.
            - Ne sois jamais accusateur. Reste neutre et informatif.
            - Exemple : "La gestion des actifs numériques comme les cryptomonnaies est un domaine complexe et en évolution. Les contrats d'assurance actuels [Passage 1] détaillent les procédures pour les fraudes informatiques classiques, mais ne mentionnent pas spécifiquement les crypto-actifs. Il est recommandé de consulter un expert pour ce type de cas spécifique."

        PASSAGES EXTRAITS DES DOCUMENTS:
        ---
        {context_str}
        ---

        QUESTION DE L'UTILISATEUR: "{question}"

        RÉPONSE NUANCÉE:
        """

        response = await self.synthesis_client.chat.completions.create(
            model=os.getenv("LLM_SYNTHESIS_MODEL", "gpt-4.1-2025-04-14"),
            messages=[{"role": "user", "content": prompt}],
            temperature=float(os.getenv("LLM_SYNTHESIS_TEMPERATURE", "0.2")),
            max_tokens=2048
        )

        answer = response.choices[0].message.content or "Une erreur est survenue lors de la génération de la réponse."

        # --- Post-traitement pour extraire les citations ---
        # On ne change pas cette logique, elle reste robuste.
        citations = []
        # Utilise une regex pour trouver les [Passage X] dans la réponse
        passage_indices = re.findall(r'\[Passage (\d+)\]', answer)
        unique_indices = sorted(list(set([int(i) - 1 for i in passage_indices])))

        for index in unique_indices:
            if 0 <= index < len(context_chunks):
                chunk = context_chunks[index]
                citations.append({
                    "documentId": chunk.get('documentId', ''),
                    "documentPath": chunk.get('documentPath', 'Source inconnue'),
                    "text": chunk['text']
                })

        # Nettoyer la réponse des marqueurs de passage pour une meilleure lisibilité
        cleaned_answer = re.sub(r'\s*\[Passage \d+\]', '', answer).strip()

        return {"answer": cleaned_answer, "citations": citations}

    # ========================================================================
    # SECTION 6 : INTERROGATION (QUERY) - Interface Principale
    # ========================================================================

    # ========================================================================
    # SECTION: ARCHITECTURE AGENTIQUE REACT (PROTOCOLE DAN v4)
    # ========================================================================

    async def _reasoning_step(self, question: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, str]:
        """
        Étape de raisonnement de l'agent ReAct avec intégration de la mémoire conversationnelle.

        PROTOCOLE DAN v5 : L'agent maintient maintenant le contexte conversationnel.
        Si la question fait référence à un élément précédent ("cette négociation", "y a-t-il des limites"),
        l'agent résout la coréférence en s'appuyant sur l'historique.

        Cette étape simule le raisonnement d'un juriste qui analyserait la question
        en tenant compte de la conversation en cours.
        """
        # Construction du contexte conversationnel
        conversation_context = ""
        if conversation_history and len(conversation_history) > 0:
            conversation_context = "\n\nCONTEXTE CONVERSATIONNEL (messages précédents) :\n"
            for msg in conversation_history[-10:]:  # Limiter aux 10 derniers messages
                role = "Utilisateur" if msg.get("role") == "user" else "Assistant"
                msg_content = msg.get("content", "")
                conversation_context += f"- {role}: {msg_content}\n"
            conversation_context += "\n"

        prompt = f"""Tu es un assistant juridique expert en recherche documentaire. Ta tâche est de décomposer la question de l'utilisateur en une requête de recherche optimisée pour un système RAG.
Identifie les concepts clés, les synonymes juridiques et les termes techniques pertinents.
{conversation_context}
Question de l'utilisateur: "{question}"

Pense étape par étape :
1. SI la question fait référence à un élément de l'historique conversationnel (ex: "cette négociation", "y a-t-il des limites", "dans ce cas"), RÉSOUS LA CORÉFÉRENCE en identifiant le sujet réel à partir du contexte.
2. Quelle est l'intention réelle de l'utilisateur ?
3. Quels sont les termes exacts à rechercher (noms propres, acronymes, numéros d'articles) ?
4. Quels synonymes ou concepts sémantiques pourraient exister dans les documents (ex: "litige" -> "réclamation", "conciliation", "médiateur") ?
5. Formule la requête de recherche la plus efficace qui combine ces éléments.

EXEMPLES :
- Si l'historique mentionne "négociation immobilière" et que la question est "y a-t-il des limites ?", la requête doit être "limites négociation immobilière notaire déontologie mandat".
- Si la question est "Quelles sont les voies de recours en cas de litige avec un notaire ?", la requête doit être "recours litige notaire réclamation conciliation médiateur chambre disciplinaire".

Réponds UNIQUEMENT en JSON avec la structure suivante :
{{
  "thought": "Ta réflexion étape par étape pour arriver à la requête, en expliquant comment tu as résolu les coréférences si applicable.",
  "search_query": "La requête de recherche finale et optimisée."
}}"""

        try:
            response = await self.planner_client.chat.completions.create(
                model=os.getenv("LLM_PLANNER_MODEL", "gpt-4.1-nano-2025-04-14"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content: Optional[str] = response.choices[0].message.content

            parsed_response: Dict[str, Any] = {}
            if content:
                try:
                    parsed_response = json.loads(content)
                except json.JSONDecodeError:
                    logger.warning("Réponse JSON invalide du planner: %s", content)

            thought = str(parsed_response.get("thought") or "Erreur de raisonnement")
            search_query = str(parsed_response.get("search_query") or question)
            return {"thought": thought, "search_query": search_query}
        except Exception as e:
            logger.error(f"  > Échec de l'étape de raisonnement: {e}")
            return {"thought": f"Exception: {e}", "search_query": question}

    async def _hybrid_search_step(
        self,
        search_query: str,
        vector_limit: int = 7,
        fulltext_limit: int = 7,
        final_limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Étape d'action de l'agent ReAct.
        Exécute une recherche hybride (vectorielle + full-text),
        fusionne les résultats et effectue un reranking final.

        Args:
            search_query: Requête optimisée par l'étape de raisonnement
            vector_limit: Nombre max de chunks vectoriels à récupérer
            fulltext_limit: Nombre max de chunks full-text à récupérer
            final_limit: Nombre final de chunks après reranking

        Returns:
            Liste des meilleurs chunks après fusion et reranking
        """
        # Génération de l'embedding pour la recherche vectorielle
        vector_embedding = await self._get_embeddings([search_query])
        if not vector_embedding:
            return []

        # Recherche parallèle : vectorielle + full-text
        vector_search_task = self.neo4j.search_chunks_by_vector(vector_embedding[0], limit=vector_limit)
        fulltext_search_task = self.neo4j.search_chunks_by_fulltext(search_query, limit=fulltext_limit)

        retrieved_chunks_vector, retrieved_chunks_fulltext = await asyncio.gather(
            vector_search_task,
            fulltext_search_task
        )
        logger.info(f"  > Récupération brute: {len(retrieved_chunks_vector)} chunks (vecteur), {len(retrieved_chunks_fulltext)} chunks (full-text).")

        # Fusion et déduplication par chunkId
        all_chunks = {chunk['chunkId']: chunk for chunk in retrieved_chunks_vector}
        for chunk in retrieved_chunks_fulltext:
            if chunk['chunkId'] not in all_chunks:
                all_chunks[chunk['chunkId']] = chunk

        fused_chunks = list(all_chunks.values())
        if not fused_chunks:
            return []

        logger.info(f"  > {len(fused_chunks)} chunks uniques fusionnés avant reranking.")

        # Reranking intelligent par LLM
        reranked_chunks = await self._rerank_chunks(search_query, fused_chunks)

        # Sélection finale
        final_chunks = reranked_chunks[:final_limit]
        logger.info(f"  > {len(final_chunks)} chunks finaux sélectionnés après reranking.")

        return final_chunks

    async def _rerank_chunks(self, question: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Utilise un LLM pour réévaluer et classer la pertinence des chunks.
        Version optimisée avec format JSON simple.
        """
        if not chunks:
            return []

        logger.info(f"  > Reranking de {len(chunks)} chunks...")

        rerank_prompt = "Voici une question et une liste de passages extraits de documents. Pour chaque passage, évalue sa pertinence pour répondre à la question sur une échelle de 0 à 10. Réponds en JSON.\n\n"
        rerank_prompt += f'Question: "{question}"\n\n'
        rerank_prompt += "Passages:\n"
        for i, chunk in enumerate(chunks):
            rerank_prompt += f"--- Passage {i} ---\n{chunk['text'][:800]}\n\n"

        rerank_prompt += 'Format de réponse JSON attendu : {"scores": [{"passage": 0, "score": 8}, {"passage": 1, "score": 2}, ...]}'

        try:
            response = await self.planner_client.chat.completions.create(
                model=os.getenv("LLM_PLANNER_MODEL", "gpt-4.1-nano-2025-04-14"),
                messages=[{"role": "user", "content": rerank_prompt}],
                temperature=float(os.getenv("LLM_PLANNER_TEMPERATURE", "0.0")),
                response_format={"type": "json_object"},
                max_tokens=2000
            )
            content = response.choices[0].message.content
            if not content:
                logger.warning("  > Reranking échoué : pas de réponse du LLM.")
                return chunks

            scores_data = json.loads(content)

            # Attacher les scores aux chunks avec gestion robuste des erreurs
            scores = {}
            if 'scores' in scores_data and isinstance(scores_data['scores'], list):
                for item in scores_data['scores']:
                    if isinstance(item, dict) and 'passage' in item and 'score' in item:
                        scores[item['passage']] = item['score']

            for i, chunk in enumerate(chunks):
                chunk['rerank_score'] = scores.get(i, 0)

            # Trier par le nouveau score
            sorted_chunks = sorted(chunks, key=lambda c: c.get('rerank_score', 0), reverse=True)

            # Log des résultats
            logger.info(f"  > Reranking terminé. Top 3 scores:")
            for i, chunk in enumerate(sorted_chunks[:3], 1):
                score = chunk.get('rerank_score', 0)
                doc = chunk.get('documentPath', 'N/A')[:50]
                logger.info(f"     {i}. Score {score}/10 - {doc}")

            return sorted_chunks

        except Exception as e:
            logger.error(f"  > Échec du reranking: {e}. Retour des chunks non classés.")
            return chunks

    async def _rerank_chunks_by_relevance(self, question: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        RERANKING INTELLIGENT : Utilise un LLM pour évaluer la pertinence de chaque chunk
        par rapport à la question et retrier les résultats.

        Cette étape est cruciale car le score de similarité vectorielle ne garantit pas
        que le chunk contient réellement la réponse à la question.
        """
        if not chunks:
            return []

        logger.info(f"  > Reranking de {len(chunks)} chunks avec LLM...")

        # Préparer les chunks pour l'évaluation
        chunks_for_eval = []
        for i, chunk in enumerate(chunks):
            chunks_for_eval.append({
                "index": i,
                "text": chunk['text'][:800],  # Limiter pour éviter les tokens excessifs
                "doc": chunk.get('documentPath', 'N/A')
            })

        # Prompt pour le LLM de reranking
        prompt = f"""
Tu es un système d'évaluation de pertinence pour un système RAG notarial.

**QUESTION DE L'UTILISATEUR:**
{question}

**CHUNKS À ÉVALUER:**
{json.dumps(chunks_for_eval, ensure_ascii=False, indent=2)}

**TÂCHE:**
Pour chaque chunk, évalue sa pertinence par rapport à la question sur une échelle de 0 à 10:
- 10: Le chunk contient directement et explicitement la réponse à la question
- 7-9: Le chunk contient des informations très pertinentes et liées à la question
- 4-6: Le chunk contient des informations contextuelles ou partiellement pertinentes
- 1-3: Le chunk est faiblement lié à la question
- 0: Le chunk n'est pas pertinent du tout

**FORMAT DE SORTIE (JSON STRICT):**
{{
  "evaluations": [
    {{"index": 0, "score": 8, "reason": "Contient la procédure exacte demandée"}},
    {{"index": 1, "score": 3, "reason": "Mentionne le sujet mais sans détails utiles"}},
    ...
  ]
}}

Réponds UNIQUEMENT avec l'objet JSON, sans texte avant ou après.
"""

        try:
            response = await self.planner_client.chat.completions.create(
                model=os.getenv("LLM_PLANNER_MODEL", "gpt-4.1-nano-2025-04-14"),
                messages=[{"role": "user", "content": prompt}],
                temperature=float(os.getenv("LLM_PLANNER_TEMPERATURE", "0.0")),
                response_format={"type": "json_object"},
                max_tokens=2000
            )

            content = response.choices[0].message.content
            if not content:
                logger.warning("  > Reranking échoué : pas de réponse du LLM, utilisation du tri par similarité.")
                return chunks

            eval_data = json.loads(content)
            evaluations = eval_data.get("evaluations", [])

            # Créer un dictionnaire index -> score
            scores_map = {e['index']: e.get('score', 0) for e in evaluations}

            # Ajouter les scores de reranking aux chunks
            for i, chunk in enumerate(chunks):
                chunk['rerank_score'] = scores_map.get(i, 0)

            # Trier par score de reranking (décroissant)
            reranked = sorted(chunks, key=lambda c: c.get('rerank_score', 0), reverse=True)

            # Log des résultats
            logger.info(f"  > Reranking terminé. Top 3 scores:")
            for i, chunk in enumerate(reranked[:3], 1):
                score = chunk.get('rerank_score', 0)
                doc = chunk.get('documentPath', 'N/A')[:50]
                logger.info(f"     {i}. Score {score}/10 - {doc}")

            return reranked

        except Exception as e:
            logger.error(f"  > Erreur lors du reranking: {e}")
            logger.warning("  > Utilisation du tri par similarité vectorielle en fallback.")
            return chunks

    async def query(self, question: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Orchestre un agent ReAct (Reason + Act) pour répondre à la question.
        PROTOCOLE DAN v5 - Architecture Agentique avec Mémoire Conversationnelle.

        L'agent ne se contente plus de chercher bêtement. Il raisonne d'abord comme un juriste :
        1. REASON : Décompose la question, identifie les synonymes juridiques ET intègre le contexte conversationnel
        2. ACT    : Exécute une recherche hybride optimisée
        3. OBSERVE: Synthétise la réponse avec les meilleurs chunks

        Cette architecture élimine le "gap sémantique" sans maintenance manuelle de synonymes
        ET maintient la cohérence contextuelle sur plusieurs tours de conversation.
        """
        logger.info(f"🚀 Requête Agentique ReAct reçue (DAN v5): '{question}'")
        if conversation_history:
            logger.info(f"  > 💭 Historique conversationnel actif : {len(conversation_history)} messages")

        # --- ÉTAPE 1: RAISONNEMENT (REASON) ---
        # L'agent réfléchit à la meilleure façon de décomposer la question.
        thought_process = await self._reasoning_step(question, conversation_history)
        search_query = thought_process.get("search_query", question)
        logger.info(f"  > 🧠 Pensée de l'agent : '{thought_process.get('thought', 'N/A')}'")
        logger.info(f"  > 🔍 Requête de recherche optimisée : '{search_query}'")

        # --- ÉTAPE 2: ACTION (ACT) ---
        # L'agent exécute la recherche hybride avec la requête optimisée.
        context_chunks = await self._hybrid_search_step(search_query)

        if not context_chunks:
            # Si la recherche échoue, on tente une dernière fois avec la question originale.
            logger.warning("  > ⚠️  La recherche optimisée a échoué. Tentative avec la question originale.")
            context_chunks = await self._hybrid_search_step(question)
            if not context_chunks:
                logger.error("  > ❌ ÉCHEC FINAL : Aucune information pertinente trouvée.")
                return {"answer": "L'information n'est pas disponible dans les documents fournis.", "citations": []}

        # --- ÉTAPE 3: OBSERVATION & SYNTHÈSE (OBSERVE & GENERATE) ---
        # L'agent observe les résultats et génère la réponse finale.
        return await self._synthesize_answer_with_citations(question, context_chunks)
    
    async def query_with_metrics(self, question: str) -> Dict[str, Any]:
        """
        Interroge la base de connaissances et retourne la réponse avec des métriques détaillées.
        Utilisé pour l'évaluation et le monitoring.
        """
        logger.info(f"🚀 Requête avec métriques: '{question}'")
        
        # Activation du Query Planner
        strategy = await self._select_rag_strategy(question)
        
        # Variables pour les métriques
        chunks_retrieved = 0
        relations_found = 0
        context = ""
        
        # Distribution des requêtes avec collecte de métriques
        if strategy == RAGStrategy.VECTOR_ONLY:
            context, chunks_retrieved = await self._execute_vector_only_with_metrics(question)
        elif strategy == RAGStrategy.GRAPH_FIRST:
            context, chunks_retrieved, relations_found = await self._execute_graph_first_with_metrics(question)
        else:  # HYBRID
            context, chunks_retrieved, relations_found = await self._execute_hybrid_with_metrics(question)

        if not context:
            answer = "Aucune information pertinente n'a pu être extraite pour répondre à cette question."
        else:
            answer = await self._synthesize_answer(question, context)
        
        return {
            "answer": answer,
            "strategy": strategy.value,
            "chunks_retrieved": chunks_retrieved,
            "relations_found": relations_found
        }
    
    async def _execute_vector_only_with_metrics(self, question: str) -> tuple[str, int]:
        """Exécute une recherche vectorielle pure avec métriques."""
        logger.info("  > Exécution VECTOR_ONLY avec métriques")
        question_embedding_list = await self._get_embeddings([question])
        if not question_embedding_list: return ("", 0)
        question_embedding = question_embedding_list[0]
        
        chunks = await self.neo4j.search_chunks_by_vector(question_embedding, limit=10)
        if not chunks: return ("", 0)
        
        context_parts = ["Contexte extrait des documents pertinents:"]
        context_parts.extend([f"- {c['text']}" for c in chunks])
        return ("\n".join(context_parts), len(chunks))
    
    async def _execute_graph_first_with_metrics(self, question: str) -> tuple[str, int, int]:
        """Exécute une recherche priorisant le graphe avec métriques."""
        logger.info("  > Exécution de la stratégie GRAPH_FIRST avec métriques...")
        entities = await self._extract_entities_from_query(question)
        if not entities or len(entities) < 2:
            logger.warning("  > Moins de 2 entités trouvées, GRAPH_FIRST inefficace. Fallback sur HYBRID.")
            return await self._execute_hybrid_with_metrics(question)
        
        logger.info(f"  > Entités identifiées : {entities}")
        paths_context = await self.neo4j.find_paths_between_entities(entities, max_depth=3)
        
        if not paths_context:
            logger.warning("  > Aucun chemin trouvé. Fallback sur HYBRID.")
            return await self._execute_hybrid_with_metrics(question)
            
        context = "Informations extraites du graphe de connaissances basé sur les entités de la question:\n"
        context += "\n".join(paths_context)
        
        # Métrique : nombre de chemins trouvés au lieu de relations
        return (context, 0, len(paths_context))
    
    async def _execute_hybrid_with_metrics(self, question: str) -> tuple[str, int, int]:
        """Exécute la stratégie hybride standard avec métriques."""
        logger.info("  > Exécution HYBRID avec métriques")
        question_embedding_list = await self._get_embeddings([question])
        if not question_embedding_list: return ("", 0, 0)
        question_embedding = question_embedding_list[0]
        
        retrieved_chunks = await self.neo4j.search_chunks_by_vector(question_embedding, limit=5)
        if not retrieved_chunks: return ("", 0, 0)

        context_parts = ["Contexte extrait des documents pertinents:"]
        context_parts.extend([f"- {c['text']}" for c in retrieved_chunks])
        chunks_count = len(retrieved_chunks)
        
        # Enrichissement par le graphe
        chunk_ids = [r['chunkId'] for r in retrieved_chunks]
        relations = await self.neo4j.get_relations_from_chunks(chunk_ids, limit=10)
        relations_count = 0
        
        if relations:
            relations_count = len(relations)
            context_parts.append("\nInformations contextuelles du graphe de connaissances:")
            for rel in relations:
                context_parts.append(f"- L'entité '{rel['entite']}' a une relation '{rel['relation']}' avec '{rel['autre_entite']}'.")
        
        return ("\n".join(context_parts), chunks_count, relations_count)

# --- Singleton ---
rag_service_instance = None
def get_rag_service() -> RAGService:
    global rag_service_instance
    if rag_service_instance is None:
        # Injection de dépendances via leurs singletons respectifs.
        rag_service_instance = RAGService(
            neo4j_service=get_neo4j_service(),
            minio_service=get_minio_service()
        )
    return rag_service_instance
