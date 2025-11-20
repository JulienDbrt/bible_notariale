# backend/src/services/ontology_service.py
import logging
from rdflib import Graph, RDFS, OWL
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

class OntologyService:
    def __init__(self, owl_file_path: str):
        self.graph = Graph()
        if not owl_file_path:
            logger.info("⚠️ Pas de fichier d'ontologie fourni. Classification ontologique désactivée.")
            self.mapping = {}
            return
            
        logger.info(f"Chargement de l'ontologie depuis {owl_file_path}...")
        try:
            self.graph.parse(owl_file_path, format="xml")
            self.mapping = self._build_mapping()
            logger.info(f"✅ Ontologie chargée. {len(self.mapping)} concepts mappés.")
        except Exception as e:
            logger.error(f"❌ ERREUR FATALE: Impossible de charger l'ontologie: {e}")
            self.mapping = {}

    def _build_mapping(self) -> Dict[str, str]:
        """Construit un dictionnaire de synonymes vers les noms de classes canoniques."""
        mapping = {}
        # Requête SPARQL pour extraire toutes les classes et leurs labels
        query = """
            SELECT ?class ?label
            WHERE {
                ?class a owl:Class .
                ?class rdfs:label ?label .
            }
        """
        results = self.graph.query(query)
        for row in results:
            # Accès sécurisé aux valeurs du tuple résultat
            if hasattr(row, '__getitem__') and hasattr(row, '__len__') and len(row) >= 2:
                class_name = str(row[0]).split('#')[-1]
                synonym = str(row[1]).lower().strip()
                mapping[synonym] = class_name
        return mapping

    def get_class_for_synonym(self, term: str) -> str | None:
        """Trouve la classe ontologique pour un terme donné. Maintenant tolérant aux None."""
        if not term or not isinstance(term, str):
            return None  # Si le terme est None ou pas une chaîne, on retourne None.
        return self.mapping.get(term.lower().strip())

# Singleton pour le service
ontology_service_instance = None
def get_ontology_service() -> OntologyService:
    global ontology_service_instance
    if ontology_service_instance is None:
        import os
        # Try multiple possible paths for the ontology file
        possible_paths = [
            "/app/ontologies/notaria_ontology.owl",  # Docker container path
            "ontologies/notaria_ontology.owl",       # Relative path
            "backend/ontologies/notaria_ontology.owl", # Original path
        ]
        
        owl_path = None
        for path in possible_paths:
            if os.path.exists(path):
                owl_path = path
                break
        
        if owl_path is None:
            logger.warning("⚠️ Ontology file not found. Service will run without ontological classification.")
            # Create a dummy service that returns None for all queries
            ontology_service_instance = OntologyService("")
        else:
            ontology_service_instance = OntologyService(owl_path)
    return ontology_service_instance