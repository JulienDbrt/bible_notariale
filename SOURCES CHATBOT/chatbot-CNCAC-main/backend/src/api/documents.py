from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from typing import List, Dict, Any, Optional
import os
import uuid
import logging
from datetime import datetime
import httpx
import asyncio
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

from ..models.schemas import DocumentResponse, DocumentStatus, APIResponse
from ..core.database import get_supabase_client
from ..services.minio_service import get_minio_service
from ..services.neo4j_service import get_neo4j_service

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = "/app/uploads"
DEFAULT_ENRICHMENT_SCRIPT = Path("/app/post-ingestion.sh")

def _locate_enrichment_script() -> Path:
    """Return the first existing enrichment script path based on env overrides and defaults."""
    candidate_strings = [
        os.getenv("POST_INGESTION_SCRIPT"),
        str(DEFAULT_ENRICHMENT_SCRIPT),
        str(Path(__file__).resolve().parents[2] / "post-ingestion.sh"),
    ]

    checked_paths = []
    for candidate in candidate_strings:
        if not candidate:
            continue
        script_path = Path(candidate).expanduser()
        checked_paths.append(str(script_path))
        if script_path.exists():
            return script_path

    raise FileNotFoundError(", ".join(checked_paths))

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    folder_path: str = Form("/"),
    supabase: Any = Depends(get_supabase_client),
    minio_service: Any = Depends(get_minio_service)
) -> DocumentResponse:
    """Upload a document, save to Minio, and start embedding process"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Get file extension and validate
    file_extension = os.path.splitext(file.filename)[1].lower()
    if not file_extension:
        raise HTTPException(status_code=400, detail="File must have an extension")
    
    # Read file content
    try:
        file_content = await file.read()
        file_size = len(file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {str(e)}")
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    
    # Create upload directory if it doesn't exist (backup local storage)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    unique_filename = f"{file_id}{file_extension}"
    local_file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file locally as backup
    try:
        with open(local_file_path, "wb") as buffer:
            buffer.write(file_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file locally: {str(e)}")
    
    # Upload to Minio
    try:
        minio_path = await minio_service.upload_file(file_content, file.filename, file_id)
    except Exception as e:
        # Clean up local file if Minio upload fails
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
        raise HTTPException(status_code=500, detail=f"Failed to upload to Minio: {str(e)}")
    
    # Normalize folder path
    if not folder_path.startswith("/"):
        folder_path = "/" + folder_path
    if not folder_path.endswith("/") and folder_path != "/":
        folder_path = folder_path + "/"

    # Create document record in database
    document_data = {
        "id": file_id,
        "user_id": user_id,
        "filename": file.filename,
        "file_extension": file_extension,
        "file_path": local_file_path,
        "minio_path": minio_path,
        "folder_path": folder_path,
        "file_size": file_size,
        "upload_date": datetime.utcnow().isoformat(),
        "indexing_status": "pending",
        "status": DocumentStatus.PENDING
    }
    
    try:
        result = supabase.table("documents").insert(document_data).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create document record")
    except Exception as e:
        # Clean up files if database insert fails
        if os.path.exists(local_file_path):
            os.remove(local_file_path)
        await minio_service.delete_file(minio_path)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Document uploaded successfully - ready for manual indexation
    
    return DocumentResponse(**document_data)

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(supabase: Any = Depends(get_supabase_client)) -> List[DocumentResponse]:
    """Get all documents with their metadata"""
    try:
        result = supabase.table("documents").select("*").order("upload_date", desc=True).execute()
        return [DocumentResponse(**doc) for doc in result.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/verify-indexing")
async def verify_document_indexing(
    supabase: Any = Depends(get_supabase_client),
    neo4j_service: Any = Depends(get_neo4j_service)
) -> Dict[str, Any]:
    """Compare Supabase indexing status with actual Neo4j indexed content"""
    try:
        # Get documents from Supabase that are marked as indexed
        supabase_result = supabase.table("documents").select("*").eq("indexing_status", "indexed").execute()
        supabase_indexed = {doc["id"]: doc for doc in supabase_result.data} if supabase_result.data else {}
        
        # Get all documents marked as any processing status for comparison
        all_supabase_result = supabase.table("documents").select("*").execute()
        all_supabase_docs = {doc["id"]: doc for doc in all_supabase_result.data} if all_supabase_result.data else {}
        
        # Get documents actually indexed in Neo4j
        neo4j_indexed = await neo4j_service.get_indexed_documents()
        # Map Neo4j docs by their document_id (which is the transformed filename)
        neo4j_docs = {doc["document_id"]: doc for doc in neo4j_indexed}
        
        # Find discrepancies
        supabase_only = []  # Marked indexed in Supabase but missing from Neo4j
        neo4j_only = []     # Exists in Neo4j but not marked as indexed in Supabase
        matched = []        # Properly indexed in both systems
        supabase_pending = []  # Documents in Supabase but not processed yet
        
        # Check Supabase indexed documents - match by transformed minio_path
        for doc_id, supabase_doc in supabase_indexed.items():
            # Extract the full path after bucket name from minio_path and transform it like protocole_operationnel.py does
            minio_path = supabase_doc.get("minio_path", "")
            if minio_path.startswith("s3://"):
                # Extract full path after bucket: s3://training-docs/CSN2021/file.pdf -> CSN2021/file.pdf
                path_parts = minio_path.split("/", 3)  # Split into ['s3:', '', 'bucket', 'path/to/file']
                if len(path_parts) > 3:
                    full_path = path_parts[3]  # Get everything after bucket name
                else:
                    full_path = supabase_doc.get("filename", "")
            else:
                full_path = supabase_doc.get("filename", "")
            
            # Apply the same transformation as in protocole_operationnel.py line 247
            transformed_id = full_path.replace('/', '_').replace('.', '_')
            
            if transformed_id in neo4j_docs:
                neo4j_doc = neo4j_docs[transformed_id]
                matched.append({
                    "document_id": doc_id,
                    "filename": supabase_doc["filename"],
                    "supabase_status": supabase_doc["indexing_status"],
                    "neo4j_document_id": transformed_id,
                    "neo4j_chunks": neo4j_doc["chunk_count"],
                    "neo4j_entities": neo4j_doc["entity_count"],
                    "last_modified": supabase_doc["upload_date"]
                })
            else:
                supabase_only.append({
                    "document_id": doc_id,
                    "filename": supabase_doc["filename"],
                    "transformed_filename": transformed_id,
                    "supabase_status": supabase_doc["indexing_status"],
                    "issue": "Marked as indexed in Supabase but missing from Neo4j"
                })
        
        # Check Neo4j documents not marked as indexed in Supabase
        # We need to find which Supabase documents correspond to each Neo4j document_id
        neo4j_to_supabase = {}
        for supabase_doc_id, supabase_doc in all_supabase_docs.items():
            minio_path = supabase_doc.get("minio_path", "")
            if minio_path.startswith("s3://"):
                path_parts = minio_path.split("/", 3)
                if len(path_parts) > 3:
                    full_path = path_parts[3]
                else:
                    full_path = supabase_doc.get("filename", "")
            else:
                full_path = supabase_doc.get("filename", "")
            transformed_id = full_path.replace('/', '_').replace('.', '_')
            neo4j_to_supabase[transformed_id] = supabase_doc

        for neo4j_doc_id, neo4j_doc in neo4j_docs.items():
            # Check if this Neo4j document corresponds to a Supabase document that's marked as indexed
            corresponding_supabase = neo4j_to_supabase.get(neo4j_doc_id)
            if corresponding_supabase and corresponding_supabase["id"] in supabase_indexed:
                # This should have been caught in the first loop, skip
                continue
            elif corresponding_supabase:
                # Found corresponding Supabase document but it's not marked as indexed
                neo4j_only.append({
                    "neo4j_document_id": neo4j_doc_id,
                    "document_id": corresponding_supabase["id"],
                    "filename": corresponding_supabase.get("filename", "Unknown"),
                    "supabase_status": corresponding_supabase["indexing_status"],
                    "neo4j_chunks": neo4j_doc["chunk_count"],
                    "neo4j_entities": neo4j_doc["entity_count"],
                    "issue": f"Indexed in Neo4j but Supabase status is '{corresponding_supabase['indexing_status']}'"
                })
            else:
                # No corresponding Supabase document found
                neo4j_only.append({
                    "neo4j_document_id": neo4j_doc_id,
                    "document_id": "unknown",
                    "filename": "Unknown (not in Supabase)",
                    "supabase_status": "missing",
                    "neo4j_chunks": neo4j_doc["chunk_count"],
                    "neo4j_entities": neo4j_doc["entity_count"],
                    "issue": "Indexed in Neo4j but missing from Supabase completely"
                })
        
        # Find pending documents in Supabase
        for doc_id, supabase_doc in all_supabase_docs.items():
            if supabase_doc["indexing_status"] in ["pending", "indexing"]:
                # Check if it's actually indexed in Neo4j using transformation
                minio_path = supabase_doc.get("minio_path", "")
                if minio_path.startswith("s3://"):
                    path_parts = minio_path.split("/", 3)
                    if len(path_parts) > 3:
                        full_path = path_parts[3]
                    else:
                        full_path = supabase_doc.get("filename", "")
                else:
                    full_path = supabase_doc.get("filename", "")
                transformed_id = full_path.replace('/', '_').replace('.', '_')
                
                if transformed_id not in neo4j_docs:
                    supabase_pending.append({
                        "document_id": doc_id,
                        "filename": supabase_doc["filename"],
                        "status": supabase_doc["indexing_status"],
                        "transformed_filename": transformed_id,
                        "upload_date": supabase_doc["upload_date"]
                    })
        
        # Calculate summary statistics
        total_supabase_indexed = len(supabase_indexed)
        total_neo4j_indexed = len(neo4j_indexed)
        total_matched = len(matched)
        total_discrepancies = len(supabase_only) + len(neo4j_only)
        
        sync_percentage = (total_matched / max(total_supabase_indexed, total_neo4j_indexed, 1)) * 100 if total_matched > 0 else 0
        
        return {
            "summary": {
                "total_supabase_indexed": total_supabase_indexed,
                "total_neo4j_indexed": total_neo4j_indexed,
                "total_matched": total_matched,
                "total_discrepancies": total_discrepancies,
                "total_pending": len(supabase_pending),
                "sync_percentage": round(sync_percentage, 2)
            },
            "matched_documents": matched,
            "discrepancies": {
                "supabase_only": supabase_only,
                "neo4j_only": neo4j_only
            },
            "pending_documents": supabase_pending,
            "verification_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify indexing: {str(e)}")

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, supabase: Any = Depends(get_supabase_client)) -> DocumentResponse:
    """Get a specific document with all metadata"""
    try:
        result = supabase.table("documents").select("*").eq("id", document_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        return DocumentResponse(**result.data[0])
    except Exception as e:
        if "Document not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.patch("/{document_id}/indexing-status")
async def update_indexing_status(
    document_id: str, 
    status: str,
    supabase: Any = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Update the indexing status of a document"""
    valid_statuses = ["pending", "indexing", "indexed", "failed"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    try:
        # Check if document exists
        doc_result = supabase.table("documents").select("id").eq("id", document_id).execute()
        if not doc_result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update indexing status
        result = supabase.table("documents").update({"indexing_status": status}).eq("id", document_id).execute()
        return {"message": f"Indexing status updated to {status}"}
    except Exception as e:
        if "Document not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/{document_id}", response_model=APIResponse)
async def delete_document(
    document_id: str, 
    supabase: Any = Depends(get_supabase_client),
    minio_service: Any = Depends(get_minio_service)
) -> APIResponse:
    """Delete a document from database, local storage, and Minio"""
    try:
        # Get document info first
        doc_result = supabase.table("documents").select("*").eq("id", document_id).execute()
        if not doc_result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = doc_result.data[0]
        
        # Delete from database
        result = supabase.table("documents").delete().eq("id", document_id).execute()
        
        # Delete local file from disk
        if os.path.exists(document["file_path"]):
            os.remove(document["file_path"])
        
        # Delete from Minio
        await minio_service.delete_file(document["minio_path"])
        
        return APIResponse(success=True, message="Document deleted successfully")
    except Exception as e:
        if "Document not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.get("/{document_id}/download")
async def download_document(
    document_id: str, 
    supabase: Any = Depends(get_supabase_client),
    minio_service: Any = Depends(get_minio_service)
) -> Any:
    """Download a document file from Minio"""
    from fastapi.responses import Response
    
    try:
        result = supabase.table("documents").select("*").eq("id", document_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = result.data[0]
        
        # Try to download from Minio first
        try:
            file_data = await minio_service.download_file(document["minio_path"])
            
            # Determine content type
            content_type = minio_service._get_content_type(document["file_extension"])
            
            return Response(
                content=file_data,
                media_type=content_type,
                headers={"Content-Disposition": f"attachment; filename={document['filename']}"}
            )
        except Exception as minio_error:
            # Fallback to local file if Minio fails
            local_file_path = document["file_path"]
            if os.path.exists(local_file_path):
                from fastapi.responses import FileResponse
                return FileResponse(
                    path=local_file_path,
                    filename=document["filename"],
                    media_type='application/octet-stream'
                )
            else:
                raise HTTPException(status_code=404, detail="File not found in storage")
                
    except Exception as e:
        if "not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Error downloading document: {str(e)}")

@router.patch("/{document_id}/move")
async def move_document_to_folder(
    document_id: str, 
    folder_path: str,
    supabase: Any = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Move a document to a different folder"""
    # Normalize folder path
    if not folder_path.startswith("/"):
        folder_path = "/" + folder_path
    if not folder_path.endswith("/") and folder_path != "/":
        folder_path = folder_path + "/"
    
    try:
        # Check if document exists
        doc_result = supabase.table("documents").select("id").eq("id", document_id).execute()
        if not doc_result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Update folder path
        result = supabase.table("documents").update({"folder_path": folder_path}).eq("id", document_id).execute()
        return {"message": f"Document moved to {folder_path}", "folder_path": folder_path}
    except Exception as e:
        if "Document not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/folders/list")
async def list_folders(supabase: Any = Depends(get_supabase_client)) -> Dict[str, Any]:
    """Get all unique folder paths from documents"""
    try:
        result = supabase.table("documents").select("folder_path").execute()
        if result.data:
            # Get unique folder paths and their parent paths
            folder_paths = set()
            for doc in result.data:
                if doc.get("folder_path"):
                    path = doc["folder_path"]
                    # Add all parent paths too
                    parts = path.strip("/").split("/")
                    current_path = "/"
                    folder_paths.add(current_path)
                    for part in parts:
                        if part:
                            current_path = current_path.rstrip("/") + "/" + part + "/"
                            folder_paths.add(current_path)
            
            return {"folders": sorted(list(folder_paths))}
        return {"folders": ["/"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.post("/start_ingestion")
async def start_ingestion_process(
    supabase: Any = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Start the ingestion process for all pending documents"""
    import asyncio
    from pathlib import Path
    
    try:
        # Get all pending documents
        result = supabase.table("documents").select("*").eq("status", "pending").execute()
        
        if not result.data:
            return {
                "success": True,
                "message": "No documents need processing",
                "documents_found": 0
            }
        
        document_count = len(result.data)
        
        # Update documents status to indicate processing has started
        supabase.table("documents").update({
            "status": "embedding",
            "indexing_status": "indexing"
        }).eq("status", "pending").execute()
        
        # Import and run the document processing directly
        try:
            # Import the DocumentProcessor class from protocole_operationnel
            import sys
            
            # Get the absolute path to the backend directory
            # current file: /path/to/backend/src/api/documents.py
            # backend root: /path/to/backend
            backend_path = Path(__file__).parent.parent.parent
            backend_path = backend_path.resolve()  # Get absolute path
            
            logger.info(f"Backend path resolved to: {backend_path}")
            
            # Add the backend root to the Python path
            if str(backend_path) not in sys.path:
                sys.path.insert(0, str(backend_path))
                logger.info(f"Added {backend_path} to Python path")
            
            # Check if the file exists
            protocole_path = backend_path / "protocole_operationnel.py"
            logger.info(f"Looking for protocole_operationnel.py at: {protocole_path}")
            
            if not protocole_path.exists():
                raise FileNotFoundError(f"protocole_operationnel.py not found at {protocole_path}")
            
            # Import the module
            logger.info("Importing protocole_operationnel module...")
            import protocole_operationnel as protocole_module
            logger.info("Successfully imported protocole_operationnel")
            
            # Initialize the processor and run it in background
            async def run_ingestion() -> None:
                try:
                    # Initialize services first
                    from ..core.service_manager import initialize_all_services
                    if not await initialize_all_services():
                        raise Exception("Failed to initialize services")
                    
                    # Create processor and run
                    processor = protocole_module.DocumentProcessor()
                    await processor.run_processing(force=False, limit=None)
                    
                except Exception as e:
                    logger.error(f"Background ingestion failed: {e}")
                    # Update failed documents back to pending
                    try:
                        supabase.table("documents").update({
                            "status": "pending",
                            "indexing_status": "pending"
                        }).eq("status", "embedding").execute()
                    except:
                        pass
            
            # Start the background task without awaiting it
            task = asyncio.create_task(run_ingestion())
            # Don't await the task - let it run in background
            
        except ImportError as e:
            raise HTTPException(status_code=500, detail=f"Failed to import processing module: {str(e)}")
        
        return {
            "success": True,
            "message": f"Started ingestion process for {document_count} documents",
            "documents_found": document_count,
            "status": "processing"
        }
        
    except Exception as e:
        # Revert status changes if subprocess failed
        try:
            supabase.table("documents").update({
                "status": "pending",
                "indexing_status": "pending"
            }).eq("status", "embedding").execute()
        except:
            pass
            
        raise HTTPException(status_code=500, detail=f"Failed to start ingestion: {str(e)}")

@router.post("/reset-stuck-documents")
async def reset_stuck_documents(
    supabase: Any = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Reset documents that are stuck in 'embedding' or 'indexing' status"""
    try:
        # Reset documents stuck in embedding status
        embedding_result = supabase.table("documents").update({
            "status": "pending",
            "indexing_status": "pending"
        }).eq("status", "embedding").execute()
        
        # Reset documents stuck in indexing status (but not complete)
        indexing_result = supabase.table("documents").update({
            "indexing_status": "pending"
        }).eq("indexing_status", "indexing").execute()
        
        embedding_count = len(embedding_result.data) if embedding_result.data else 0
        indexing_count = len(indexing_result.data) if indexing_result.data else 0
        
        return {
            "success": True,
            "message": f"Reset {embedding_count} embedding documents and {indexing_count} indexing documents",
            "embedding_reset": embedding_count,
            "indexing_reset": indexing_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset stuck documents: {str(e)}")

@router.post("/sync-minio")
async def sync_documents_from_minio(
    user_id: str = Form(...),
    supabase: Any = Depends(get_supabase_client),
    minio_service: Any = Depends(get_minio_service)
) -> Dict[str, Any]:
    """Synchronize Supabase documents table with actual MinIO bucket content"""
    import os
    from datetime import datetime
    
    try:
        # Get all objects from MinIO bucket
        objects = minio_service.list_files()
        
        # Get all documents from Supabase
        supabase_result = supabase.table("documents").select("*").execute()
        existing_docs = {doc["minio_path"]: doc for doc in supabase_result.data} if supabase_result.data else {}
        
        synced_count = 0
        added_count = 0
        removed_count = 0
        
        # Track MinIO objects we find
        minio_paths = set()
        
        for obj in objects:
            # Construct the MinIO path as stored in DB
            minio_path = f"s3://{minio_service.bucket_name}/{obj.object_name}"
            minio_paths.add(minio_path)
            
            # If document doesn't exist in Supabase, add it
            if minio_path not in existing_docs:
                # Extract filename from object name (remove UUID prefix if present)
                filename = obj.object_name
                if len(filename.split('.')) >= 2:
                    # Try to extract original filename (UUID.extension format)
                    parts = filename.split('.')
                    if len(parts[0]) == 36:  # UUID length
                        # This is likely a UUID-prefixed file, keep as is
                        display_name = filename
                    else:
                        display_name = filename
                else:
                    display_name = filename
                
                # Get file extension
                file_extension = os.path.splitext(filename)[1].lower()
                
                # Generate proper UUID for the document
                import uuid
                document_id = str(uuid.uuid4())
                
                # Extract folder path from object name
                if '/' in obj.object_name:
                    folder_parts = obj.object_name.split('/')[:-1]  # All parts except filename
                    folder_path = '/' + '/'.join(folder_parts) + '/'
                else:
                    folder_path = '/'
                
                # Create document record
                document_data = {
                    "id": document_id,
                    "user_id": user_id,
                    "filename": display_name,
                    "file_extension": file_extension,
                    "file_path": f"/app/uploads/{obj.object_name}",  # Local path (may not exist)
                    "minio_path": minio_path,
                    "folder_path": folder_path,
                    "file_size": obj.size,
                    "upload_date": obj.last_modified.isoformat() if obj.last_modified else datetime.utcnow().isoformat(),
                    "indexing_status": "pending",
                    "status": "pending"
                }
                
                try:
                    supabase.table("documents").insert(document_data).execute()
                    added_count += 1
                except Exception as e:
                    print(f"Warning: Failed to add document {filename}: {str(e)}")
            else:
                synced_count += 1
        
        # Remove documents from Supabase that don't exist in MinIO
        for minio_path, doc in existing_docs.items():
            if minio_path not in minio_paths:
                try:
                    supabase.table("documents").delete().eq("id", doc["id"]).execute()
                    removed_count += 1
                except Exception as e:
                    print(f"Warning: Failed to remove document {doc['filename']}: {str(e)}")
        
        return {
            "success": True,
            "message": "Documents synchronized successfully",
            "stats": {
                "total_minio_objects": len(minio_paths),
                "synced_existing": synced_count,
                "added_new": added_count,
                "removed_orphaned": removed_count
            },
            "bucket_name": minio_service.bucket_name,
            "sync_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync documents: {str(e)}")

@router.get("/ingestion/status")
async def get_ingestion_status(
    supabase: Any = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Get the current ingestion status across all documents"""
    try:
        # Get document status counts
        docs_result = supabase.table("documents").select("status, indexing_status").execute()
        
        # Get ingestion tracking status
        try:
            ingestion_result = supabase.table("document_ingestion_status").select("status").execute()
            ingestion_data = ingestion_result.data if ingestion_result.data else []
        except:
            ingestion_data = []
        
        document_counts = {
            "pending": 0,
            "embedding": 0,
            "complete": 0,
            "failed": 0
        }
        
        indexing_counts = {
            "pending": 0,
            "indexing": 0,
            "indexed": 0,
            "failed": 0
        }
        
        if docs_result.data:
            for doc in docs_result.data:
                status = doc.get("status", "pending")
                indexing_status = doc.get("indexing_status", "pending")
                
                if status in document_counts:
                    document_counts[status] += 1
                if indexing_status in indexing_counts:
                    indexing_counts[indexing_status] += 1
        
        ingestion_status_counts: Dict[str, int] = {}
        for item in ingestion_data:
            status = item.get("status", "unknown")
            ingestion_status_counts[status] = ingestion_status_counts.get(status, 0) + 1
        
        is_processing = (
            document_counts["embedding"] > 0 or 
            indexing_counts["indexing"] > 0 or
            ingestion_status_counts.get("processing", 0) > 0
        )
        
        return {
            "total_documents": len(docs_result.data) if docs_result.data else 0,
            "document_status": document_counts,
            "indexing_status": indexing_counts,
            "ingestion_tracking": ingestion_status_counts,
            "is_processing": is_processing,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ingestion status: {str(e)}")

@router.post("/sync-indexing-status")
async def sync_indexing_status_with_neo4j(
    supabase: Any = Depends(get_supabase_client),
    neo4j_service: Any = Depends(get_neo4j_service)
) -> Dict[str, Any]:
    """Update Supabase indexing status to match what's actually indexed in Neo4j"""
    try:
        # Get documents actually indexed in Neo4j
        neo4j_indexed = await neo4j_service.get_indexed_documents()
        neo4j_docs = {doc["document_id"]: doc for doc in neo4j_indexed}
        
        # Get all Supabase documents
        all_supabase_result = supabase.table("documents").select("*").execute()
        all_supabase_docs = all_supabase_result.data if all_supabase_result.data else []
        
        updated_count = 0
        
        for supabase_doc in all_supabase_docs:
            # Skip if already marked as both indexed and complete
            if supabase_doc["indexing_status"] == "indexed" and supabase_doc["status"] == "complete":
                continue
                
            # Extract the full path and transform it like protocole_operationnel.py does
            minio_path = supabase_doc.get("minio_path", "")
            if minio_path.startswith("s3://"):
                path_parts = minio_path.split("/", 3)
                if len(path_parts) > 3:
                    full_path = path_parts[3]
                else:
                    full_path = supabase_doc.get("filename", "")
            else:
                full_path = supabase_doc.get("filename", "")
            
            transformed_id = full_path.replace('/', '_').replace('.', '_')
            
            # If this document is indexed in Neo4j, update both statuses in Supabase
            if transformed_id in neo4j_docs:
                supabase.table("documents").update({
                    "indexing_status": "indexed",
                    "status": "complete"
                }).eq("id", supabase_doc["id"]).execute()
                updated_count += 1
        
        return {
            "success": True,
            "message": f"Updated {updated_count} documents to indexed/complete status",
            "updated_count": updated_count,
            "total_neo4j_indexed": len(neo4j_indexed),
            "sync_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync indexing status: {str(e)}")

@router.get("/graph/knowledge")
async def get_knowledge_graph_data(
    limit: int = 300,
    neo4j_service: Any = Depends(get_neo4j_service)
) -> Dict[str, Any]:
    """Get knowledge graph data from Neo4j for visualization

    Args:
        limit: Maximum number of nodes to retrieve (default: 300)

    Returns:
        Dictionary containing nodes, edges, and statistics for graph visualization
    """
    try:
        # Get real knowledge graph data from Neo4j
        graph_data = await neo4j_service.get_knowledge_graph(limit=limit)

        return {
            "nodes": graph_data["nodes"],
            "edges": graph_data["edges"],
            "total_nodes": len(graph_data["nodes"]),
            "total_edges": len(graph_data["edges"]),
            "statistics": graph_data["statistics"],
            "last_updated": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to retrieve knowledge graph: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve knowledge graph: {str(e)}")

@router.get("/{document_id}/metadata")
async def get_document_metadata(document_id: str, supabase: Any = Depends(get_supabase_client)) -> Dict[str, Any]:
    """Get detailed metadata for a document"""
    try:
        result = supabase.table("documents").select("*").eq("id", document_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = result.data[0]
        
        # Add file size in human readable format
        def format_file_size(size_bytes: int) -> str:
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024**2:
                return f"{size_bytes/1024:.1f} KB"
            elif size_bytes < 1024**3:
                return f"{size_bytes/(1024**2):.1f} MB"
            else:
                return f"{size_bytes/(1024**3):.1f} GB"
        
        metadata = {
            "id": document["id"],
            "filename": document["filename"],
            "file_extension": document["file_extension"],
            "file_size": document["file_size"],
            "file_size_formatted": format_file_size(document["file_size"]),
            "upload_date": document["upload_date"],
            "indexing_status": document["indexing_status"],
            "processing_status": document["status"],
            "minio_path": document["minio_path"],
            "has_local_backup": os.path.exists(document["file_path"])
        }
        
        return metadata
    except Exception as e:
        if "Document not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/start-enrichment")
async def start_enrichment_process() -> Dict[str, Any]:
    """Start the post-ingestion semantic enrichment process"""
    try:
        # Run the post-ingestion script as a background process
        try:
            script_path = _locate_enrichment_script()
        except FileNotFoundError as missing_paths:
            checked = missing_paths.args[0] if missing_paths.args else "No paths checked"
            raise HTTPException(
                status_code=500,
                detail=f"Enrichment script not found (checked: {checked})"
            )
        
        # Run the script in background
        async def run_enrichment() -> None:
            try:
                logger.info("Starting background enrichment process...")
                process = await asyncio.create_subprocess_exec(
                    "bash", str(script_path),
                    cwd=str(script_path.parent),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    logger.info("Enrichment process completed successfully")
                    logger.info(f"Enrichment output: {stdout.decode()}")
                else:
                    logger.error(f"Enrichment process failed with return code {process.returncode}")
                    logger.error(f"Error output: {stderr.decode()}")
                    
            except Exception as e:
                logger.error(f"Background enrichment failed: {e}")
        
        # Start the background task
        task = asyncio.create_task(run_enrichment())
        
        return {
            "success": True,
            "message": "Semantic enrichment process started in background",
            "status": "processing"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start enrichment: {str(e)}")
