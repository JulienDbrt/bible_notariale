import logging
from src.services.minio_service import get_minio_service
from src.services.neo4j_service import get_neo4j_service
from src.services.notaria_rag_service import get_rag_service

logger = logging.getLogger(__name__)

async def initialize_all_services() -> bool:
    """
    Processus centralisé de démarrage.
    Initialise tous les services critiques dans le bon ordre.
    """
    print("--- PROCESSUS DE DÉMARRAGE CENTRALISÉ ---")
    logger.info("--- PROCESSUS DE DÉMARRAGE CENTRALISÉ ---")
    
    # L'ordre est important. Les bases de données d'abord.
    try:
        print("  > Initialisation de Neo4j...")
        logger.info("  > Initialisation de Neo4j...")
        neo4j = get_neo4j_service()
        await neo4j.initialize()
        print("  > ✅ Neo4j opérationnel.")
        logger.info("  > ✅ Neo4j opérationnel.")

        print("  > Initialisation de MinIO...")
        logger.info("  > Initialisation de MinIO...")
        minio = get_minio_service()
        await minio.initialize()
        print("  > ✅ MinIO opérationnel.")
        logger.info("  > ✅ MinIO opérationnel.")

        # Le service RAG est initialisé en dernier, car il dépend des autres.
        print("  > Vérification du service RAG...")
        logger.info("  > Vérification du service RAG...")
        get_rag_service() # S'assure que l'instance est créée.
        print("  > ✅ Service RAG prêt.")
        logger.info("  > ✅ Service RAG prêt.")
        
        print("--- ✅ TOUS LES SYSTÈMES SONT OPÉRATIONNELS ---")
        logger.info("--- ✅ TOUS LES SYSTÈMES SONT OPÉRATIONNELS ---")
        return True

    except Exception as e:
        print(f"❌ ÉCHEC CRITIQUE DU DÉMARRAGE. PROCESSUS INTERROMPU. Erreur: {e}")
        logger.error(f"❌ ÉCHEC CRITIQUE DU DÉMARRAGE. PROCESSUS INTERROMPU. Erreur: {e}", exc_info=True)
        return False