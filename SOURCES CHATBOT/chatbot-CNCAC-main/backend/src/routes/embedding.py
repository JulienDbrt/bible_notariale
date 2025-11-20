from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from ..core.database import get_supabase_client
from ..models.schemas import UserResponse
from ..api.auth import get_current_user_from_token

router = APIRouter(prefix="/embedding", tags=["embedding"])

@router.post("/start")
async def start_embedding_process(
    current_user: UserResponse = Depends(get_current_user_from_token),
    supabase: Any = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Start the embedding process for all pending documents for the current user"""
    try:
        # Get all documents that need embedding for the current user
        result = supabase.table("documents").select("*").eq("status", "pending").eq("user_id", current_user.id).execute()
        
        if not result.data:
            return {
                "success": True,
                "message": "No documents need embedding",
                "documents_processed": 0
            }
        
        document_count = len(result.data)
        
        # Update all pending documents to embedding status
        update_result = supabase.table("documents").update({
            "status": "embedding",
            "indexing_status": "indexing"
        }).eq("status", "pending").eq("user_id", current_user.id).execute()
        
        return {
            "success": True,
            "message": f"Started embedding process for {document_count} documents",
            "documents_processed": document_count,
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start embedding: {str(e)}")

@router.post("/start/{document_id}")
async def start_embedding_for_document(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user_from_token),
    supabase: Any = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Start the embedding process for a specific document"""
    try:
        # Check if document exists and belongs to user
        result = supabase.table("documents").select("*").eq("id", document_id).eq("user_id", current_user.id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = result.data[0]
        
        # Update document status to start embedding
        update_result = supabase.table("documents").update({
            "status": "embedding",
            "indexing_status": "indexing"
        }).eq("id", document_id).execute()
        
        if not update_result.data:
            raise HTTPException(status_code=500, detail="Failed to update document status")
        
        return {
            "success": True,
            "message": f"Started embedding process for document: {document['filename']}",
            "document_id": document_id,
            "status": "started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start embedding: {str(e)}")

@router.get("/status")
async def get_embedding_status(
    current_user: UserResponse = Depends(get_current_user_from_token),
    supabase: Any = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Get the status of embedding processes for current user"""
    try:
        # Get counts of documents by status for the current user
        all_docs = supabase.table("documents").select("status").eq("user_id", current_user.id).execute()
        
        status_counts = {
            "pending": 0,
            "embedding": 0,
            "complete": 0,
            "failed": 0
        }
        
        if all_docs.data:
            for doc in all_docs.data:
                status = doc.get("status", "pending")
                if status in status_counts:
                    status_counts[status] += 1
        
        return {
            "total_documents": len(all_docs.data) if all_docs.data else 0,
            "status_counts": status_counts,
            "is_processing": status_counts["embedding"] > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get embedding status: {str(e)}")

@router.get("/status/{document_id}")
async def get_document_embedding_status(
    document_id: str,
    current_user: UserResponse = Depends(get_current_user_from_token),
    supabase: Any = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Get the embedding status for a specific document"""
    try:
        # Check if document exists and belongs to user
        result = supabase.table("documents").select("*").eq("id", document_id).eq("user_id", current_user.id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        document = result.data[0]
        
        return {
            "document_id": document_id,
            "filename": document["filename"],
            "status": document["status"],
            "indexing_status": document.get("indexing_status", "pending"),
            "upload_date": document["upload_date"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get embedding status: {str(e)}")