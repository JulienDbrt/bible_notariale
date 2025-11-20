import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
# Charger le fichier .env depuis le bon chemin
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

import asyncio
import logging
from src.services.ontology_service import get_ontology_service
from src.services.neo4j_service import get_neo4j_service

logger = logging.getLogger(__name__)

async def main():
    print("🚀 DOCTRINE CORTEX MARK II - LANCEMENT DE LA PASSE DE DENSIFICATION")
    
    ontology_service = get_ontology_service()
    neo4j_service = get_neo4j_service()
    await neo4j_service.initialize()
    
    driver = neo4j_service.get_driver()
    async with driver.session() as session:
        print("🔍 Récupération des nœuds non classifiés...")
        # On cible les nœuds 'Entity' qui n'ont pas encore de label ontologique
        result = await session.run("MATCH (n:Entity) WHERE size(labels(n)) = 1 RETURN n.nom AS name, n.type AS type")
        nodes_to_classify = await result.data()
        
        print(f"✅ {len(nodes_to_classify)} nœuds à classifier.")
        classified_count = 0
        
        for node in nodes_to_classify:
            node_name = node['name']
            node_type = node.get('type')  # Utiliser .get() pour éviter les KeyError
            
            # Tenter de classifier via le nom et le type
            ont_class_from_name = ontology_service.get_class_for_synonym(node_name)
            
            # NOUVELLE VÉRIFICATION : Ne chercher par type que si le type existe
            ont_class_from_type = None
            if node_type:
                ont_class_from_type = ontology_service.get_class_for_synonym(node_type)
            
            # On privilégie la classification la plus spécifique
            final_class = ont_class_from_name or ont_class_from_type
            
            if final_class:
                print(f"  > Classification : '{node_name}' ({node_type}) -> :{final_class}")
                # Exécution de la requête de classification
                cypher_query = f"MATCH (n:Entity {{nom: $name}}) SET n:{final_class}"
                await session.run(cypher_query, name=node_name)
                classified_count += 1

    print(f"\n🏁 DENSIFICATION TERMINÉE. {classified_count} nœuds enrichis.")
    await neo4j_service.close()

if __name__ == "__main__":
    asyncio.run(main())