#!/usr/bin/env python3
"""
PROCESSUS D'INGESTION DE DOCUMENTS - PHASE 1 : ANALYSEUR
Fonction: Scanner, analyser, et traiter les documents pour le service RAG.
"""
import asyncio
from functools import partial

async def run_sync(func, *args, **kwargs):
    """Exécute une fonction synchrone dans un thread executor."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, partial(func, *args, **kwargs))

import os
import time
import logging
import hashlib
import argparse
from typing import Tuple, Dict, Optional
from dotenv import load_dotenv
from io import BytesIO
from pathlib import Path
import fitz # PyMuPDF
from email import policy
from email.parser import BytesParser

# --- CONFIGURATION INITIALE ---
# Load environment variables from .env file before anything else
load_dotenv()
# Ajout du chemin parent pour les imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- IMPORTS DES SERVICES CRITIQUES ---
from src.services.minio_service import get_minio_service
from src.core.database import get_supabase # Renommé pour la clarté
from src.services.notaria_rag_service import get_rag_service # SERVICE RAG UNIFIÉ
from src.services.neo4j_service import get_neo4j_service
from docling.document_converter import DocumentConverter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

MIN_CONTENT_LENGTH = 100

class DocumentProcessor:
    """Le pipeline d'ingestion brute."""
    def __init__(self):
        self.minio_service = get_minio_service()
        self.supabase = get_supabase()
        self.rag_service = get_rag_service() # Utilise le service RAG unifié
        self.neo4j_service = get_neo4j_service()
        self.converter = DocumentConverter()
        self.tracking_table = "document_ingestion_status"
        self.bucket_name = os.getenv("MINIO_BUCKET_NAME", "training-docs")
        
    def _extract_text_with_docling(self, filename: str, file_bytes: bytes) -> Tuple[str, Dict]:
        """Utilise Docling pour extraire le texte propre. VERSION CORRIGÉE."""
        try:
            # La méthode correcte pour Docling v2.x est .convert() avec un DocumentStream.
            from docling_core.types.io import DocumentStream # Assurer l'import local
            
            doc_stream = DocumentStream(name=filename, stream=BytesIO(file_bytes))
            
            result = self.converter.convert(doc_stream)
            
            text_content = result.document.export_to_markdown()
            
            page_count = 0
            has_tables = False
            if hasattr(result.document, 'pages') and isinstance(result.document.pages, list):
                page_count = len(result.document.pages)
                # Defensive check: ensure 'p' is an object with a 'tables' attribute before access
                has_tables = any(hasattr(p, 'tables') and getattr(p, 'tables') for p in result.document.pages)
            else:
                page_count = 1 if text_content else 0
                has_tables = False

            metadata = {
                "docling_version": "2.x",
                "page_count": page_count,
                "has_tables": has_tables,
            }
            return text_content, metadata
            
        except Exception as e:
            logger.error(f"❌ Erreur d'extraction Docling pour {filename}: {e}")
            return "", {"error": str(e)}

    def _parse_eml_file(self, filename: str, file_bytes: bytes) -> Tuple[str, Dict]:
        """
        NOUVEL OUTIL : Parseur chirurgical pour les fichiers .eml.
        Extrait les métadonnées et le corps du message.
        """
        logger.info(f"  > Détection Email. Activation du parseur EML.")
        try:
            # Utilise BytesParser avec la politique par défaut pour gérer l'encodage
            msg = BytesParser(policy=policy.default).parsebytes(file_bytes)

            # Extraction des métadonnées clés
            subject = msg.get('subject', 'Sans objet')
            from_ = msg.get('from', 'Inconnu')
            to = msg.get('to', 'Inconnu')
            date = msg.get('date', 'Date inconnue')

            # Construction d'un en-tête contextuel
            header_text = (
                f"--- Début de l'Email ---\n"
                f"Sujet: {subject}\n"
                f"De: {from_}\n"
                f"À: {to}\n"
                f"Date: {date}\n"
                f"----------------------\n\n"
            )

            body_text = ""
            # Parcourt les différentes parties du message pour trouver le corps en texte brut
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get('Content-Disposition'))
                    
                    if content_type == 'text/plain' and 'attachment' not in content_disposition:
                        body_text = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                        break # On prend le premier corps en texte brut trouvé
            else:
                # Si ce n'est pas multipart, le corps est directement dans le payload
                body_text = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8', errors='ignore')

            full_content = header_text + body_text.strip() + "\n\n--- Fin de l'Email ---"
            
            metadata = {
                "extraction_method": "eml_parser",
                "email_subject": str(subject),
                "email_from": str(from_),
                "email_to": str(to),
                "email_date": str(date)
            }
            
            return full_content, metadata

        except Exception as e:
            logger.error(f"❌ Erreur du parseur EML pour {filename}: {e}")
            return "", {"error": str(e), "extraction_method": "eml_parser_failed"}

    def _pre_scan_pdf_for_text(self, file_bytes: bytes) -> bool:
        """ÉCLAIREUR : Détecte rapidement si un PDF contient du texte natif."""
        import fitz  # PyMuPDF
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_found = False
            # On ne scanne que les 5 premières pages pour un diagnostic rapide.
            for page in doc.pages(stop=5):
                if page.get_text("text").strip():
                    text_found = True
                    break
            doc.close()
            return text_found
        except Exception as e:
            logger.warning(f"  > Échec de l'éclaireur PyMuPDF : {e}. On utilisera l'artillerie lourde par défaut.")
            return False # En cas de doute, on suppose que c'est une image.

    async def _check_already_processed(self, filename: str, file_hash: str) -> bool:
        """Vérifie si un fichier a déjà été traité avec succès."""
        res = await run_sync(
            self.supabase.table(self.tracking_table).select("status").eq("file_hash", file_hash).execute
        )
        if res.data and res.data[0]['status'] == 'success':
            logger.info(f"⏭️ Cible déjà traitée et connue. Hash: {file_hash[:8]}...")
            return True
        return False

    async def process_single_file(self, filename: str, force: bool = False, index: int = 0, total_docs: int = 1):
        """Traite un seul fichier avec la méthode de traitement rapide."""
        logger.info(f"--- [{(index)+1}/{total_docs}] Engagement de la cible : {filename} ---")
        
        try:
            # ... (le code de téléchargement et de hash reste le même) ...
            response = self.minio_service.client.get_object(self.bucket_name, filename)
            content = response.read()
            response.close()
            response.release_conn()
            file_hash = hashlib.sha256(content).hexdigest()

            if not force and await self._check_already_processed(filename, file_hash):
                return

            await run_sync(
                self.supabase.table(self.tracking_table).upsert({"filename": filename, "file_hash": file_hash, "status": "processing"}, on_conflict="filename").execute
            )
        except Exception as e:
            if "Resource temporarily unavailable" in str(e):
                logger.warning(f"  > Connexion HTTP surchargée pour {filename}, réessai dans 2s...")
                await asyncio.sleep(2)
                return await self.process_single_file(filename, force, index, total_docs)
            logger.error(f"  > Erreur lors du traitement initial de {filename}: {e}")
            return
        
        # --- MÉTHODE DE TRAITEMENT RAPIDE ---
        text = ""
        metadata = {}
        file_extension = Path(filename).suffix.lower()
        
        try:
            if file_extension == '.eml':
                # Traitement spécialisé pour les emails
                text, metadata = self._parse_eml_file(filename, content)
            
            elif file_extension == '.pdf':
                # Logique PDF existante avec PyMuPDF
                import fitz # PyMuPDF
                doc = fitz.open(stream=content, filetype='pdf')
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()
                metadata = {"extraction_method": "PyMuPDF_fast"}

                # Si PyMuPDF n'a rien trouvé, c'est un scan. On sort le bélier (Docling avec OCR).
                if len(text.strip()) < MIN_CONTENT_LENGTH:
                    logger.warning(f"  > Éclaireur PyMuPDF inefficace. Déploiement du bélier (Docling+OCR)...")
                    text, metadata = self._extract_text_with_docling(filename, content)
                    metadata["extraction_method"] = "Docling_OCR"
            
            else:
                # Pour tous les autres formats, on utilise directement Docling
                logger.info(f"  > Format {file_extension}. Utilisation de Docling comme parseur.")
                text, metadata = self._extract_text_with_docling(filename, content)
                metadata["extraction_method"] = "Docling_default"
                
        except Exception as e:
            # Fallback final sur Docling en cas d'échec
            logger.warning(f"  > Erreur lors du parsing ({e}). Fallback sur Docling.")
            text, metadata = self._extract_text_with_docling(filename, content)
            metadata["extraction_method"] = "Docling_fallback"
        # --- Fin du traitement ---

        # ... (le reste du code : contrôle qualité, transmission au RAG, etc. reste le même) ...
        if len(text) < MIN_CONTENT_LENGTH:
            logger.warning(f"⚠️ Cible rejetée: contenu insuffisant ({len(text)} chars).")
            await run_sync(
                self.supabase.table(self.tracking_table).update({"status": "invalid", "error_message": "Contenu insuffisant"}).eq("filename", filename).execute
            )
            return
            
        logger.info(f"  > Transmission de {len(text)} caractères pour analyse initiale...")
        success = await self.rag_service.ingest_raw_document(
            document_id=filename.replace('/', '_').replace('.', '_'),
            file_path=filename,
            text_content=text
        )
        
        if success:
            logger.info(f"  ✅ Analyse brute réussie.")
            await run_sync(
                self.supabase.table(self.tracking_table).update({"status": "success", "metadata": metadata}).eq("filename", filename).execute
            )
        else:
            logger.error(f"  ❌ Échec de l'analyse brute.")
            await run_sync(
                self.supabase.table(self.tracking_table).update({"status": "error", "error_message": "Échec de l'ingestion brute RAG"}).eq("filename", filename).execute
            )

    async def purge_all_data(self):
        """PURGE SYNCHRONISÉE : Rase Neo4j ET le journal de bord Supabase."""
        logger.warning("!!! ORDRE DE PURGE TOTALE REÇU !!!")
        
        logger.info("  > Purge de la base de connaissances Neo4j...")
        await self.neo4j_service.purge_database()
        logger.info("  > ✅ Base de connaissances anéantie.")

        logger.info("  > Purge du journal de bord Supabase...")
        try:
            await run_sync(
                self.supabase.table(self.tracking_table).delete().neq("status", "never_delete").execute
            )
            logger.info("  > ✅ Journal de bord réinitialisé.")
        except Exception as e:
            logger.error(f"  > ❌ Échec de la purge Supabase : {e}")

        logger.warning("!!! PURGE TOTALE TERMINÉE !!!")

    async def run_processing(self, force: bool = False, limit: Optional[int] = None):
        """
        Exécute un traitement complet des documents sur MinIO en parallèle.
        """
        # Limite le nombre d'opérations simultanées pour ne pas saturer la machine.
        # C'est une variable critique à ajuster en fonction des ressources.
        CONCURRENCY_LIMIT = 2
        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

        logger.info(f"🔍 Lancement du traitement parallèle (concurrence: {CONCURRENCY_LIMIT})...")
        
        if not self.minio_service.client:
            logger.warning("Client MinIO non initialisé. Tentative d'initialisation manuelle...")
            await self.minio_service.initialize()
            if not self.minio_service.client:
                logger.error("Échec critique de l'initialisation du client MinIO. Arrêt du traitement.")
                return

        all_files = self.minio_service.client.list_objects(self.bucket_name, recursive=True)
        # On ne garde que les fichiers, pas les répertoires fantômes
        files_to_process = [file_obj for file_obj in all_files if not file_obj.is_dir]
        
        if limit and limit > 0:
            logger.info(f"Limitation du traitement à {limit} documents.")
            files_to_process = files_to_process[:limit]

        total_docs = len(files_to_process)

        async def worker(file_obj, index):
            """Chaque worker est une escouade autonome."""
            async with semaphore:
                logger.info(f"  > Escouade {index+1} engagée sur la cible {file_obj.object_name}")
                await self.process_single_file(file_obj.object_name, force, index, total_docs)

        if not files_to_process:
            logger.info("Aucune cible valide trouvée dans le bucket.")
            return

        # Création des escouades (tâches)
        tasks = [worker(file_obj, i) for i, file_obj in enumerate(files_to_process)]
        
        # Lancement de l'assaut simultané
        start_time = time.time()
        logger.info(f"💥 Déploiement de {len(tasks)} escouades. Assaut en cours...")
        await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # Récupération des statistiques Neo4j
        neo4j_stats = await self.neo4j_service.get_statistics()
        
        logger.info("="*60)
        logger.info("📊 RAPPORT DE TRAITEMENT PARALLÈLE")
        logger.info("="*60)
        logger.info("📁 TRAITEMENT DES DOCUMENTS:")
        logger.info(f"  - Documents traités: {total_docs}")
        logger.info(f"  - Temps total de l'opération: {total_time:.2f} secondes ({total_time/60:.1f} minutes)")
        avg_time = total_time / total_docs if total_docs > 0 else 0
        logger.info(f"  - Vitesse effective: {avg_time:.2f} secondes par document")
        logger.info("")
        logger.info("🗃️ BASE DE CONNAISSANCES NEO4J:")
        logger.info(f"  - Nœuds totaux: {neo4j_stats['nodes']}")
        logger.info(f"  - Documents indexés: {neo4j_stats['documents']}")
        logger.info(f"  - Chunks créés: {neo4j_stats['chunks']}")
        logger.info(f"  - Relations établies: {neo4j_stats['relations']}")
        logger.info("="*60)

async def main():
    parser = argparse.ArgumentParser(description="Phase 1 : Processeur de documents")
    parser.add_argument('--force', action='store_true', help="Forcer le retraitement de tous les documents.")
    parser.add_argument('--limit', type=int, default=None, help="Limiter le nombre de fichiers à traiter.")
    parser.add_argument('--purge', action='store_true', help="Purger la base de données Neo4j avant le traitement.")
    args = parser.parse_args()

    # NOUVEL IMPORT
    from src.core.service_manager import initialize_all_services

    print("🚀 PROCESSUS D'INGESTION DE DOCUMENTS - PHASE 1")
    print("===================================================")
    
    # NOUVELLE PROCÉDURE DE DÉMARRAGE
    if not await initialize_all_services():
        exit(1) # Si le démarrage échoue, arrêt du processus.

    processor = DocumentProcessor()

    if args.purge:
        # NOUVEL APPEL À LA PURGE SYNCHRONISÉE
        await processor.purge_all_data()

    await processor.run_processing(force=args.force, limit=args.limit)

    # La fermeture est gérée par les services eux-mêmes si nécessaire, ou à la fin du script.
    # On peut créer une fonction de fermeture dans le service_manager si besoin.

if __name__ == "__main__":
    asyncio.run(main())