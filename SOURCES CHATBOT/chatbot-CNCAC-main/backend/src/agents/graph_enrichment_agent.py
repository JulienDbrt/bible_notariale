#!/usr/bin/env python3
"""
AGENT D'ENRICHISSEMENT DU GRAPHE - ANALYSE INTELLIGENTE
Service d'analyse automatique pour l'enrichissement autonome du graphe
"""
import asyncio
import logging
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import openai
from ..services.neo4j_service import get_neo4j_service
from ..core.config import settings
from ..core.database import get_supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphEnrichmentAgent:
    """
    Agent autonome d'enrichissement du graphe de connaissances
    Fonction: Analyser, inférer et enrichir les relations dans le graphe
    """
    
    def __init__(self) -> None:
        self.neo4j_service = get_neo4j_service()
        self.supabase = get_supabase()
        
        # Configuration LLM pour l'analyse
        self.llm_client = openai.AsyncOpenAI(
            api_key=settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        
        # Statistiques de l'agent
        self.stats: Dict[str, Any] = {
            "inferences_created": 0,
            "syntheses_generated": 0,
            "anomalies_detected": 0,
            "cycles_completed": 0,
            "corrections_processed": 0,
            "feedback_analyzed": 0,
            "last_run": None
        }
    
    async def initialize(self) -> None:
        """Initialise l'agent et ses connexions"""
        await self.neo4j_service.initialize()
        logger.info("🕵️ Agent d'enrichissement initialisé")
    
    async def run_inference_cycle(self, limit: int = 10) -> Dict[str, Any]:
        """
        🔄 Cycle d'inférence principal
        Analyse le graphe et propose de nouvelles relations
        """
        logger.info(f"🔄 Démarrage du cycle d'inférence (limite: {limit})")
        cycle_stats: Dict[str, Any] = {
            "started_at": datetime.utcnow().isoformat(),
            "new_inferences": 0,
            "patterns_found": 0,
            "corrections_applied": 0,
            "feedback_processed": 0,
            "errors": 0
        }
        
        driver = self.neo4j_service.get_driver()
        
        try:
            async with driver.session() as session:
                # 1. RECHERCHE DE PATTERNS TRANSITIFS
                # Si A->B et B->C, peut-on inférer A->C ?
                transitive_patterns = await session.run("""
                    MATCH (a)-[r1]->(b)-[r2]->(c)
                    WHERE NOT (a)-[]-(c)
                    AND type(r1) = type(r2)
                    AND labels(a) = labels(c)
                    RETURN 
                        a.nom AS entity_a,
                        b.nom AS entity_b,
                        c.nom AS entity_c,
                        type(r1) AS relation_type,
                        labels(a) AS entity_type
                    LIMIT $limit
                """, limit=limit)
                
                transitive_candidates = await transitive_patterns.data()
                
                for candidate in transitive_candidates:
                    # Demander au LLM de valider l'inférence
                    inference_valid = await self._validate_transitive_inference(candidate)
                    
                    if inference_valid:
                        # Créer la nouvelle relation inférée
                        await self._create_inferred_relation(
                            session,
                            candidate['entity_a'],
                            candidate['entity_c'],
                            candidate['relation_type'],
                            f"Inféré via {candidate['entity_b']}"
                        )
                        cycle_stats['new_inferences'] += 1
                
                # 2. RECHERCHE DE CO-OCCURRENCES
                # Entités souvent mentionnées ensemble sans relation explicite
                # Note: Les entités sont liées aux documents, pas directement aux chunks
                cooccurrence_patterns = await session.run("""
                    MATCH (e1:Entity)-[:MENTIONED_IN]->(d:Document)
                    MATCH (e2:Entity)-[:MENTIONED_IN]->(d)
                    WHERE e1 <> e2 
                    AND NOT (e1)-[]-(e2)
                    WITH e1, e2, COUNT(d) AS cooccurrence_count
                    WHERE cooccurrence_count >= 2
                    RETURN 
                        e1.nom AS entity1,
                        e2.nom AS entity2,
                        cooccurrence_count,
                        labels(e1) AS type1,
                        labels(e2) AS type2
                    ORDER BY cooccurrence_count DESC
                    LIMIT $limit
                """, limit=limit)
                
                cooccurrences = await cooccurrence_patterns.data()
                
                for cooc in cooccurrences:
                    # Analyser la nature de la relation potentielle
                    relation_suggestion = await self._analyze_cooccurrence(cooc)
                    
                    if relation_suggestion:
                        await self._create_suggested_relation(
                            session,
                            cooc['entity1'],
                            cooc['entity2'],
                            relation_suggestion['type'],
                            relation_suggestion['confidence']
                        )
                        cycle_stats['patterns_found'] += 1
                
                # 3. SYNTHÈSE DES NŒUDS IMPORTANTS
                # Générer des résumés pour les nœuds avec haute connectivité
                important_nodes = await session.run("""
                    MATCH (n)
                    WITH n, COUNT{(n)-[]->()} + COUNT{()<-[]-(n)} AS degree
                    WHERE degree >= 5
                    AND (COALESCE(n.summary, '') = '' OR COALESCE(n.last_synthesis, datetime('1970-01-01')) < datetime() - duration('P7D'))
                    RETURN 
                        COALESCE(n.nom, '') AS name,
                        COALESCE(n.description, '') AS description,
                        labels(n) AS types,
                        degree
                    ORDER BY degree DESC
                    LIMIT $limit
                """, limit=limit//2)  # Moins de synthèses car plus coûteux
                
                nodes_to_synthesize = await important_nodes.data()
                
                for node in nodes_to_synthesize:
                    synthesis = await self._generate_node_synthesis(session, node['name'])
                    
                    if synthesis:
                        await session.run("""
                            MATCH (n {nom: $name})
                            SET n.summary = $summary,
                                n.last_synthesis = datetime(),
                                n.synthesis_version = COALESCE(n.synthesis_version, 0) + 1
                        """, name=node['name'], summary=synthesis)
                        
                        cycle_stats['new_inferences'] += 1
                        logger.info(f"📝 Synthèse générée pour: {node['name']}")
                
                # 4. TRAITEMENT DU FEEDBACK NÉGATIF
                feedback_stats = await self.process_negative_feedback(limit)
                cycle_stats['feedback_processed'] = feedback_stats['processed']
                cycle_stats['corrections_applied'] = feedback_stats['corrections']
                
        except Exception as e:
            logger.error(f"❌ Erreur dans le cycle d'inférence: {e}")
            cycle_stats['errors'] += 1
        
        # Mise à jour des statistiques
        self.stats['inferences_created'] += cycle_stats['new_inferences']
        self.stats['cycles_completed'] += 1
        self.stats['last_run'] = datetime.utcnow().isoformat()
        
        cycle_stats['completed_at'] = datetime.utcnow().isoformat()
        logger.info(f"✅ Cycle terminé: {cycle_stats}")
        
        return cycle_stats
    
    async def _validate_transitive_inference(self, pattern: Dict[str, Any]) -> bool:
        """
        Valide une inférence transitive avec le LLM
        """
        prompt = f"""
        Analyse cette relation transitive potentielle dans un contexte notarial:
        
        - {pattern['entity_a']} --[{pattern['relation_type']}]--> {pattern['entity_b']}
        - {pattern['entity_b']} --[{pattern['relation_type']}]--> {pattern['entity_c']}
        
        Question: Peut-on logiquement inférer que:
        {pattern['entity_a']} --[{pattern['relation_type']}]--> {pattern['entity_c']} ?
        
        Réponds uniquement par OUI ou NON suivi d'une brève justification.
        """
        
        try:
            response = await self.llm_client.chat.completions.create(
                model=os.getenv("LLM_EXTRACTION_MODEL", "gpt-4.1-mini-2025-04-14"),
                messages=[
                    {"role": "system", "content": "Tu es un expert en logique et en droit notarial."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            content = response.choices[0].message.content
            if content:
                answer = content.upper()
                return "OUI" in answer[:10]  # Cherche OUI dans les premiers caractères
            return False
            
        except Exception as e:
            logger.error(f"Erreur validation inférence: {e}")
            return False
    
    async def _analyze_cooccurrence(self, cooc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyse une co-occurrence pour suggérer une relation
        """
        prompt = f"""
        Deux entités apparaissent ensemble {cooc['cooccurrence_count']} fois dans les documents:
        - Entité 1: {cooc['entity1']} (type: {cooc['type1']})
        - Entité 2: {cooc['entity2']} (type: {cooc['type2']})
        
        Suggère UNE relation probable entre ces entités.
        
        Réponds en JSON:
        {{
            "type": "nom_de_la_relation",
            "confidence": 0.0 à 1.0,
            "justification": "brève explication"
        }}
        """
        
        try:
            response = await self.llm_client.chat.completions.create(
                model=os.getenv("LLM_EXTRACTION_MODEL", "gpt-4.1-mini-2025-04-14"),
                messages=[
                    {"role": "system", "content": "Tu es un expert en analyse de relations dans le domaine notarial."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                return None
            suggestion = json.loads(content)
            
            # Filtrer les suggestions peu confiantes
            if suggestion.get('confidence', 0) >= 0.6:
                return suggestion if isinstance(suggestion, dict) else None
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur analyse co-occurrence: {e}")
            return None
    
    async def _generate_node_synthesis(self, session: Any, node_name: str) -> Optional[str]:
        """
        Génère une synthèse complète pour un nœud important
        """
        # Récupérer toutes les relations du nœud
        result = await session.run("""
            MATCH (n {nom: $name})
            OPTIONAL MATCH (n)-[r]-(related)
            RETURN 
                n.description AS node_desc,
                collect(DISTINCT {
                    type: type(r),
                    direction: CASE WHEN startNode(r) = n THEN 'OUT' ELSE 'IN' END,
                    target: related.nom,
                    target_desc: related.description
                }) AS relations
        """, name=node_name)
        
        data = await result.single()
        
        if not data:
            return None
        
        # Construire le contexte pour la synthèse
        context = f"Entité: {node_name}\n"
        if data['node_desc']:
            context += f"Description actuelle: {data['node_desc']}\n"
        
        context += "\nRelations:\n"
        for rel in data['relations'][:20]:  # Limiter pour le prompt
            if rel['target']:
                direction = "→" if rel['direction'] == 'OUT' else "←"
                context += f"- {rel['type']} {direction} {rel['target']}"
                if rel['target_desc']:
                    context += f" ({rel['target_desc']})"
                context += "\n"
        
        prompt = f"""
        Génère une synthèse concise et informative pour cette entité notariale.
        La synthèse doit capturer l'essence de l'entité et ses relations principales.
        
        {context}
        
        Synthèse (max 200 mots):
        """
        
        try:
            response = await self.llm_client.chat.completions.create(
                model=os.getenv("LLM_SYNTHESIS_MODEL", "gpt-4.1-2025-04-14"),
                messages=[
                    {"role": "system", "content": "Tu es un expert notarial qui crée des synthèses précises et utiles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erreur génération synthèse: {e}")
            return None
    
    async def _create_inferred_relation(self, session: Any, entity_a: str, entity_b: str, 
                                       relation_type: str, inference_path: str) -> None:
        """
        Crée une relation inférée dans le graphe
        """
        try:
            await session.run("""
                MATCH (a {nom: $entity_a})
                MATCH (b {nom: $entity_b})
                CREATE (a)-[r:INFERRED {
                    original_type: $relation_type,
                    inference_path: $inference_path,
                    created_at: datetime(),
                    confidence: 0.8,
                    agent: 'GraphEnrichmentAgent'
                }]->(b)
            """, entity_a=entity_a, entity_b=entity_b, 
                relation_type=relation_type, inference_path=inference_path)
            
            logger.info(f"✅ Relation inférée créée: {entity_a} --[INFERRED:{relation_type}]--> {entity_b}")
            
        except Exception as e:
            logger.error(f"Erreur création relation inférée: {e}")
    
    async def _create_suggested_relation(self, session: Any, entity1: str, entity2: str,
                                        relation_type: str, confidence: float) -> None:
        """
        Crée une relation suggérée (à valider) dans le graphe
        """
        try:
            await session.run("""
                MATCH (a {nom: $entity1})
                MATCH (b {nom: $entity2})
                CREATE (a)-[r:SUGGESTED {
                    suggested_type: $relation_type,
                    confidence: $confidence,
                    created_at: datetime(),
                    status: 'pending_validation',
                    agent: 'GraphEnrichmentAgent'
                }]->(b)
            """, entity1=entity1, entity2=entity2,
                relation_type=relation_type, confidence=confidence)
            
            logger.info(f"💡 Relation suggérée: {entity1} --[SUGGESTED:{relation_type}]--> {entity2} (conf: {confidence})")
            
        except Exception as e:
            logger.error(f"Erreur création relation suggérée: {e}")
    
    async def detect_anomalies(self, limit: int = 20) -> List[Dict]:
        """
        🔍 Détecte les anomalies dans le graphe
        - Nœuds isolés
        - Cycles suspects
        - Contradictions
        """
        anomalies = []
        driver = self.neo4j_service.get_driver()
        
        async with driver.session() as session:
            # 1. Nœuds isolés (aucune relation)
            isolated = await session.run("""
                MATCH (n)
                WHERE NOT (n)-[]-()
                RETURN n.nom AS name, labels(n) AS types
                LIMIT $limit
            """, limit=limit)
            
            isolated_nodes = await isolated.data()
            for node in isolated_nodes:
                anomalies.append({
                    "type": "isolated_node",
                    "entity": node['name'],
                    "severity": "low",
                    "message": f"Nœud isolé sans relations: {node['name']}"
                })
            
            # 2. Cycles courts suspects
            cycles = await session.run("""
                MATCH (a)-[r1]->(b)-[r2]->(c)-[r3]->(a)
                WHERE a <> b AND b <> c AND a <> c
                RETURN a.nom AS node_a, b.nom AS node_b, c.nom AS node_c,
                       type(r1) AS rel1, type(r2) AS rel2, type(r3) AS rel3
                LIMIT $limit
            """, limit=limit//2)
            
            cyclic_patterns = await cycles.data()
            for cycle in cyclic_patterns:
                anomalies.append({
                    "type": "circular_dependency",
                    "entities": [cycle['node_a'], cycle['node_b'], cycle['node_c']],
                    "severity": "medium",
                    "message": f"Cycle détecté: {cycle['node_a']} -> {cycle['node_b']} -> {cycle['node_c']} -> {cycle['node_a']}"
                })
            
            # 3. Relations contradictoires
            contradictions = await session.run("""
                MATCH (a)-[r1]->(b)
                MATCH (b)-[r2]->(a)
                WHERE type(r1) = type(r2)
                AND type(r1) IN ['PROPRIÉTAIRE_DE', 'PARENT_DE', 'SUPÉRIEUR_DE']
                RETURN a.nom AS entity_a, b.nom AS entity_b, type(r1) AS relation
                LIMIT $limit
            """, limit=limit//2)
            
            contradictory_rels = await contradictions.data()
            for contra in contradictory_rels:
                anomalies.append({
                    "type": "contradictory_relation",
                    "entities": [contra['entity_a'], contra['entity_b']],
                    "severity": "high",
                    "message": f"Relation contradictoire: {contra['entity_a']} et {contra['entity_b']} ont une relation '{contra['relation']}' bidirectionnelle"
                })
        
        self.stats['anomalies_detected'] += len(anomalies)
        logger.info(f"🔍 {len(anomalies)} anomalies détectées")
        
        return anomalies
    
    async def validate_suggested_relations(self, auto_approve_threshold: float = 0.9) -> None:
        """
        ✅ Valide ou rejette les relations suggérées
        """
        driver = self.neo4j_service.get_driver()
        
        async with driver.session() as session:
            # Auto-approuver les suggestions à haute confiance
            auto_approved = await session.run("""
                MATCH ()-[r:SUGGESTED]->()
                WHERE r.confidence >= $threshold
                AND r.status = 'pending_validation'
                SET r.status = 'auto_approved',
                    r.validated_at = datetime()
                RETURN COUNT(r) AS count
            """, threshold=auto_approve_threshold)
            
            result = await auto_approved.single()
            count = result['count'] if result else 0
            
            if count > 0:
                logger.info(f"✅ {count} relations auto-approuvées (seuil: {auto_approve_threshold})")
            
            # Convertir les relations approuvées en relations réelles
            await session.run("""
                MATCH (a)-[r:SUGGESTED]->(b)
                WHERE r.status = 'auto_approved'
                CREATE (a)-[new:RELATION {
                    type: r.suggested_type,
                    created_from: 'suggestion',
                    created_at: datetime(),
                    confidence: r.confidence
                }]->(b)
                DELETE r
            """)
    
    async def process_negative_feedback(self, limit: int = 5) -> Dict[str, int]:
        """
        🔍 Traite les feedbacks négatifs pour améliorer le graphe
        """
        stats = {"processed": 0, "corrections": 0}
        
        try:
            # Récupérer les feedbacks négatifs non traités
            response = self.supabase.table("evaluations").select(
                "id, conversation_id, question, response, feedback, comment, sources, created_at"
            ).eq("feedback", "negative").is_("processed", None).limit(limit).execute()
            
            feedbacks = response.data if response.data else []
            
            for feedback in feedbacks:
                logger.info(f"🔍 Traitement du feedback négatif #{feedback['id']}")
                
                # Analyser le feedback avec le LLM
                correction = await self._analyze_feedback_for_correction(feedback)
                
                if correction:
                    # Créer un nœud CorrectionNeeded dans Neo4j
                    await self._create_correction_node(feedback, correction)
                    stats['corrections'] += 1
                
                # Marquer le feedback comme traité
                self.supabase.table("evaluations").update(
                    {"processed": True, "processed_at": datetime.utcnow().isoformat()}
                ).eq("id", feedback['id']).execute()
                
                stats['processed'] += 1
                
            if stats['processed'] > 0:
                logger.info(f"✅ {stats['processed']} feedbacks traités, {stats['corrections']} corrections créées")
                self.stats['feedback_analyzed'] += stats['processed']
                self.stats['corrections_processed'] += stats['corrections']
                
        except Exception as e:
            logger.error(f"❌ Erreur traitement feedback: {e}")
            
        return stats
    
    async def _analyze_feedback_for_correction(self, feedback: Dict[str, Any]) -> Optional[Dict]:
        """
        Analyse un feedback négatif avec le LLM pour identifier les corrections nécessaires
        """
        prompt = f"""
        Un expert notarial a signalé une réponse incorrecte. Analyse ce feedback pour identifier les corrections nécessaires dans le graphe de connaissances.
        
        Question de l'utilisateur: {feedback['question']}
        
        Réponse de l'IA (jugée incorrecte): {feedback['response']}
        
        Commentaire de l'expert: {feedback.get('comment', 'Pas de commentaire')}
        
        Sources utilisées: {feedback.get('sources', 'Non disponibles')}
        
        Identifie :
        1. Le type d'erreur (factuelle, relationnelle, contextuelle)
        2. Les entités ou relations potentiellement erronées
        3. La correction suggérée
        
        Réponds en JSON:
        {{
            "error_type": "type d'erreur",
            "affected_entities": ["liste des entités concernées"],
            "problematic_relations": ["relations potentiellement erronées"],
            "correction_suggestion": "description de la correction à apporter",
            "confidence": 0.0 à 1.0,
            "severity": "low|medium|high|critical"
        }}
        """
        
        try:
            response = await self.llm_client.chat.completions.create(
                model=os.getenv("LLM_SYNTHESIS_MODEL", "gpt-4.1-2025-04-14"),
                messages=[
                    {"role": "system", "content": "Tu es un expert en analyse d'erreurs dans les systèmes de RAG notariaux."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                return None
            correction = json.loads(content)
            
            # Ne retourner que les corrections avec une confiance suffisante
            if correction.get('confidence', 0) >= 0.5:
                return correction if isinstance(correction, dict) else None
                
        except Exception as e:
            logger.error(f"Erreur analyse feedback: {e}")
            
        return None
    
    async def _create_correction_node(self, feedback: Dict[str, Any], correction: Dict[str, Any]) -> None:
        """
        Crée un nœud CorrectionNeeded dans Neo4j pour tracer la correction
        """
        driver = self.neo4j_service.get_driver()
        
        try:
            async with driver.session() as session:
                # Créer le nœud CorrectionNeeded
                await session.run("""
                    CREATE (c:CorrectionNeeded {
                        feedback_id: $feedback_id,
                        question: $question,
                        incorrect_response: $response,
                        expert_comment: $comment,
                        error_type: $error_type,
                        correction_suggestion: $suggestion,
                        severity: $severity,
                        confidence: $confidence,
                        created_at: datetime(),
                        status: 'pending',
                        agent: 'GraphEnrichmentAgent'
                    })
                    RETURN c
                """, 
                    feedback_id=feedback['id'],
                    question=feedback['question'],
                    response=feedback['response'],
                    comment=feedback.get('comment', ''),
                    error_type=correction['error_type'],
                    suggestion=correction['correction_suggestion'],
                    severity=correction['severity'],
                    confidence=correction['confidence']
                )
                
                # Lier aux entités affectées si identifiées
                for entity in correction.get('affected_entities', []):
                    await session.run("""
                        MATCH (e {nom: $entity_name})
                        MATCH (c:CorrectionNeeded {feedback_id: $feedback_id})
                        CREATE (c)-[:AFFECTS]->(e)
                    """, entity_name=entity, feedback_id=feedback['id'])
                
                # Marquer les relations problématiques si identifiées
                for relation in correction.get('problematic_relations', []):
                    await session.run("""
                        MATCH ()-[r]-()
                        WHERE type(r) = $relation_type
                        WITH r LIMIT 10
                        SET r.potentially_incorrect = true,
                            r.flagged_by_feedback = $feedback_id,
                            r.flagged_at = datetime()
                    """, relation_type=relation, feedback_id=feedback['id'])
                
                logger.info(f"📝 Nœud CorrectionNeeded créé pour feedback #{feedback['id']} (severity: {correction['severity']})")
                
        except Exception as e:
            logger.error(f"Erreur création nœud correction: {e}")
    
    async def apply_corrections(self, auto_apply_threshold: float = 0.8) -> None:
        """
        ✅ Applique automatiquement les corrections à haute confiance
        """
        driver = self.neo4j_service.get_driver()
        
        async with driver.session() as session:
            # Récupérer les corrections en attente
            corrections = await session.run("""
                MATCH (c:CorrectionNeeded {status: 'pending'})
                WHERE c.confidence >= $threshold
                AND c.severity IN ['high', 'critical']
                RETURN c
                ORDER BY c.severity DESC, c.created_at
                LIMIT 10
            """, threshold=auto_apply_threshold)
            
            corrections_data = await corrections.data()
            
            for corr in corrections_data:
                correction = corr['c']
                
                # Appliquer la correction selon le type d'erreur
                if correction['error_type'] == 'factuelle':
                    # Marquer les documents sources comme peu fiables
                    # Note: Les entités sont liées aux documents, pas aux chunks
                    await session.run("""
                        MATCH (c:CorrectionNeeded {feedback_id: $feedback_id})
                        MATCH (c)-[:AFFECTS]->(e:Entity)
                        MATCH (e)-[:MENTIONED_IN]->(d:Document)
                        SET d.reliability_score = COALESCE(d.reliability_score, 1.0) * 0.5,
                            d.flagged_as_unreliable = true,
                            d.flagged_reason = $reason
                    """, 
                        feedback_id=correction['feedback_id'],
                        reason=correction['correction_suggestion']
                    )
                    
                elif correction['error_type'] == 'relationnelle':
                    # Supprimer ou affaiblir les relations erronées
                    await session.run("""
                        MATCH ()-[r]-()
                        WHERE r.flagged_by_feedback = $feedback_id
                        SET r.confidence = COALESCE(r.confidence, 1.0) * 0.3,
                            r.is_disputed = true,
                            r.dispute_reason = $reason
                    """,
                        feedback_id=correction['feedback_id'],
                        reason=correction['correction_suggestion']
                    )
                
                # Marquer la correction comme appliquée
                await session.run("""
                    MATCH (c:CorrectionNeeded {feedback_id: $feedback_id})
                    SET c.status = 'applied',
                        c.applied_at = datetime()
                """, feedback_id=correction['feedback_id'])
                
                logger.info(f"✅ Correction appliquée pour feedback #{correction['feedback_id']}")
    
    async def run_continuous(self, interval_minutes: int = 30, max_cycles: int | None = None) -> None:
        """
        🔄 Exécution continue de l'agent
        """
        logger.info(f"🤖 Agent démarré en mode continu (intervalle: {interval_minutes} min)")
        
        cycles_run = 0
        while max_cycles is None or cycles_run < max_cycles:
            try:
                # Cycle d'inférence
                cycle_stats = await self.run_inference_cycle()
                
                # Détection d'anomalies (toutes les 3 cycles)
                if cycles_run % 3 == 0:
                    anomalies = await self.detect_anomalies()
                    if anomalies:
                        logger.warning(f"⚠️ {len(anomalies)} anomalies détectées")
                
                # Validation des suggestions (toutes les 2 cycles)
                if cycles_run % 2 == 0:
                    await self.validate_suggested_relations()
                
                # Application des corrections (toutes les 4 cycles)
                if cycles_run % 4 == 0:
                    await self.apply_corrections()
                
                cycles_run += 1
                
                # Attendre avant le prochain cycle
                logger.info(f"💤 Attente de {interval_minutes} minutes avant le prochain cycle...")
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Arrêt demandé par l'utilisateur")
                break
            except Exception as e:
                logger.error(f"❌ Erreur dans le cycle continu: {e}")
                await asyncio.sleep(60)  # Attente courte en cas d'erreur
        
        logger.info(f"🏁 Agent terminé après {cycles_run} cycles")
        logger.info(f"📊 Statistiques finales: {self.stats}")
    
    async def close(self) -> None:
        """Ferme proprement les connexions"""
        await self.neo4j_service.close()
        logger.info("👋 Agent fermé")


async def main() -> None:
    """Point d'entrée principal pour l'agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent d'enrichissement du graphe")
    parser.add_argument('--continuous', action='store_true', help='Mode continu')
    parser.add_argument('--interval', type=int, default=30, help='Intervalle en minutes (mode continu)')
    parser.add_argument('--cycles', type=int, help='Nombre max de cycles (mode continu)')
    parser.add_argument('--limit', type=int, default=10, help='Limite d\'éléments par cycle')
    args = parser.parse_args()
    
    agent = GraphEnrichmentAgent()
    await agent.initialize()
    
    try:
        if args.continuous:
            await agent.run_continuous(args.interval, args.cycles)
        else:
            # Un seul cycle
            stats = await agent.run_inference_cycle(args.limit)
            print(f"\n📊 Résultats du cycle:")
            print(json.dumps(stats, indent=2))
            
            # Détection d'anomalies
            anomalies = await agent.detect_anomalies()
            if anomalies:
                print(f"\n⚠️ Anomalies détectées:")
                for anomaly in anomalies:
                    print(f"  - [{anomaly['severity']}] {anomaly['message']}")
    
    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(main())