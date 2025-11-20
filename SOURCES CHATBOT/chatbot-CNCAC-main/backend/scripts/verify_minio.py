#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier le contenu d'un bucket MinIO.
OBJECTIF : Obtenir un décompte fiable des objets.
"""
import os
from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error

# Chemin vers le fichier .env, en partant du script et en remontant d'un niveau
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    print(f"⚠️ AVERTISSEMENT : Fichier .env non trouvé à l'emplacement attendu : {env_path}")

# --- CONFIGURATION ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET = os.getenv("MINIO_BUCKET_NAME", "training-docs") # Utilise la var d'env, fallback sur training-docs
MINIO_SECURE = os.getenv("MINIO_SECURE", "true").lower() == "true"

def main():
    """Point d'entrée du script de vérification."""
    print("--- OPÉRATION OEIL DE MINIO ---")
    print(f"📡 Cible : Endpoint '{MINIO_ENDPOINT}', Bucket '{MINIO_BUCKET}'")

    if not all([MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY]):
        print("❌ ERREUR: Variables d'environnement MinIO manquantes (ENDPOINT, ROOT_USER, ROOT_PASSWORD).")
        return

    try:
        # Initialisation du client MinIO
        client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )

        # Vérification de l'existence du bucket
        found = client.bucket_exists(MINIO_BUCKET)
        if not found:
            print(f"❌ ERREUR: Le bucket '{MINIO_BUCKET}' n'existe pas ou vous n'y avez pas accès.")
            return
        
        print(f"✅ Bucket '{MINIO_BUCKET}' trouvé.")
        print("🔍 Lancement du décompte récursif des objets...")

        # Comptage des objets
        objects = client.list_objects(MINIO_BUCKET, recursive=True)
        object_count = 0
        for obj in objects:
            object_count += 1
            # Décommenter pour voir tous les fichiers
            # print(f"  -> {obj.object_name}")

        print("\n--- RAPPORT D'ANALYSE ---")
        print(f"📊 Nombre total d'objets trouvés dans '{MINIO_BUCKET}': {object_count}")
        print("--------------------------")

        if object_count == 244:
            print("✅ SUCCÈS : Le décompte correspond aux attentes (244). Le problème se situe dans le script reindex.py.")
        elif object_count == 28:
            print("⚠️ ÉCHEC PARTIEL : Le décompte est de 28. Le problème pourrait être la structure du bucket ou les permissions de la clé API.")
        else:
            print(f"ℹ️ INFO : Le décompte est de {object_count}. Incohérence avec les deux scénarios attendus.")

    except S3Error as exc:
        print(f"❌ ERREUR S3: Une erreur de communication avec le serveur MinIO est survenue.")
        print(f"   Détails: {exc}")
    except Exception as exc:
        print(f"❌ ERREUR INCONNUE: {exc}")

if __name__ == "__main__":
    main()