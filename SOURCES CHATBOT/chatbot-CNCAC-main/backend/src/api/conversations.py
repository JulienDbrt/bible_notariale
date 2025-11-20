from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import uuid
import json
from datetime import datetime

from ..models.schemas import ConversationResponse, ConversationCreate, MessageResponse, APIResponse, UserResponse
from ..core.database import get_supabase_client
from .auth import get_current_user_from_token

router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    supabase: Any = Depends(get_supabase_client)
) -> ConversationResponse:
    """Create a new conversation"""
    conversation_id = str(uuid.uuid4())
    conversation_data = {
        "id": conversation_id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "created_date": datetime.utcnow().isoformat()
    }

    try:
        result = supabase.table("conversations").insert(conversation_data).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create conversation")
        # Convertir la date string en datetime pour le modèle de réponse
        response_data: Dict[str, Any] = conversation_data.copy()
        if isinstance(response_data['created_date'], str):
            response_data['created_date'] = datetime.fromisoformat(response_data['created_date'].replace('Z', '+00:00'))
        return ConversationResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    current_user: UserResponse = Depends(get_current_user_from_token),
    supabase: Any = Depends(get_supabase_client)
) -> List[ConversationResponse]:
    """Get all conversations for current user"""
    try:
        result = supabase.table("conversations").select("*").eq("user_id", current_user.id).order("created_date", desc=True).execute()
        return [ConversationResponse(**conv) for conv in result.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    supabase: Any = Depends(get_supabase_client)
) -> ConversationResponse:
    """Get a specific conversation"""
    try:
        result = supabase.table("conversations").select("*").eq("id", conversation_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return ConversationResponse(**result.data[0])
    except Exception as e:
        if "Conversation not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    supabase: Any = Depends(get_supabase_client)
) -> List[MessageResponse]:
    """Get all messages in a conversation"""
    try:
        # First check if conversation exists
        conv_result = supabase.table("conversations").select("id").eq("id", conversation_id).execute()
        if not conv_result.data:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get messages
        result = supabase.table("messages").select("*").eq("conversation_id", conversation_id).order("timestamp", desc=False).execute()
        messages = []
        for msg in result.data:
            # Gérer la désérialisation du champ 'citations' qui est stocké en JSONB/string
            if isinstance(msg.get('citations'), str):
                msg['citations'] = json.loads(msg['citations'])
            elif msg.get('citations') is None:
                msg['citations'] = []
            messages.append(MessageResponse(**msg))
        return messages
    except Exception as e:
        if "Conversation not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/{conversation_id}", response_model=APIResponse)
async def delete_conversation(
    conversation_id: str,
    supabase: Any = Depends(get_supabase_client)
) -> APIResponse:
    """Delete a conversation and all its messages"""
    try:
        # Check if conversation exists
        conv_result = supabase.table("conversations").select("id").eq("id", conversation_id).execute()
        if not conv_result.data:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Delete messages first (foreign key constraint)
        supabase.table("messages").delete().eq("conversation_id", conversation_id).execute()

        # Delete conversation
        supabase.table("conversations").delete().eq("id", conversation_id).execute()

        return APIResponse(success=True, message="Conversation deleted successfully")
    except Exception as e:
        if "Conversation not found" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")
