# backend/src/core/database.py - VERSION DE COMMANDEMENT FINALE
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

# Assurer que les variables d'environnement sont chargées
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)

# --- CONFIGURATION DIRECTE ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- INSTANCE SINGLETON ---
supabase_client_instance: Client | None = None

def get_supabase() -> Client:
    """
    Crée et retourne une instance singleton du client Supabase.
    Valide l'existence de la table critique.
    """
    global supabase_client_instance

    if supabase_client_instance is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Configuration Supabase manquante dans le .env.")
        
        try:
            logger.info("🔌 Création de la connexion singleton Supabase...")
            supabase_client_instance = create_client(SUPABASE_URL, SUPABASE_KEY)
            
            # --- PHASE DE DIAGNOSTIC ---
            logger.info("    > Vérification du schéma de la base de données...")
            supabase_client_instance.table("document_ingestion_status").select("id").limit(1).execute()
            logger.info("    > ✅ Schéma Supabase validé.")

        except Exception as e:
            if "relation \"public.document_ingestion_status\" does not exist" in str(e):
                logger.error("❌ ERREUR FATALE : La table 'document_ingestion_status' est manquante.")
                logger.error("   > La structure de base de la Forteresse Sémantique n'a pas été construite.")
                print("\n" + "="*80)
                print("ORDRE D'OPÉRATIONS POUR L'OPÉRATEUR :")
                print("1. Accédez à votre terminal Docker pour le conteneur 'supabase-db'.")
                print("2. Lancez 'psql -U postgres'.")
                print("3. Copiez et collez le contenu du fichier : backend/migrations/create_tracking_table.sql")
                print("4. Exécutez le script SQL, puis quittez psql avec '\\q'.")
                print("5. Relancez l'opération après l'exécution du script.")
                print("="*80)
                exit(1) # Arrêt propre et direct.
            else:
                logger.error(f"❌ Échec de la connexion ou de la validation Supabase : {e}")
                raise e
            
    return supabase_client_instance

def get_supabase_client() -> Client:
    """Dependency function for FastAPI, returns the same singleton instance."""
    return get_supabase()

async def init_db() -> Client:
    """Initialize database connection - ensures singleton is created"""
    try:
        client = get_supabase()
        logger.info("✅ Database initialization completed")
        return client
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise e