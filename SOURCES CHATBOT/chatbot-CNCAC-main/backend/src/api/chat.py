from fastapi import APIRouter, HTTPException, Depends
from typing import Any
import uuid
from datetime import datetime

from ..models.schemas import ChatRequest, ChatResponse, Citation, MessageCreate, ConversationCreate, UserResponse
from ..core.database import get_supabase_client
from ..services.notaria_rag_service import get_rag_service
from .auth import get_current_user_from_token

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user_from_token),
    supabase: Any = Depends(get_supabase_client),
    rag_service: Any = Depends(get_rag_service)
) -> ChatResponse:
    """Send a message and get AI response"""
    conversation_id = request.conversation_id

    # Create new conversation if none provided
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

        # Generate title from first message (truncated)
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message

        conversation_data = {
            "id": conversation_id,
            "user_id": current_user.id,
            "title": title,
            "created_date": datetime.utcnow().isoformat()
        }

        try:
            result = supabase.table("conversations").insert(conversation_data).execute()
            if not result.data:
                raise HTTPException(status_code=500, detail="Failed to create conversation")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")

    # Verify conversation exists if ID was provided
    else:
        try:
            conv_result = supabase.table("conversations").select("id").eq("id", conversation_id).execute()
            if not conv_result.data:
                raise HTTPException(status_code=404, detail="Conversation not found")
        except Exception as e:
            if "Conversation not found" in str(e):
                raise e
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Save user message
    user_message_id = str(uuid.uuid4())
    user_message_data = {
        "id": user_message_id,
        "conversation_id": conversation_id,
        "content": request.message,
        "is_user": True,
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        result = supabase.table("messages").insert(user_message_data).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save user message")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving user message: {str(e)}")

    # Retrieve conversation history for context-aware responses (DAN v5)
    conversation_history = []
    if conversation_id:
        try:
            # Récupérer les 10 derniers messages de la conversation
            history_result = supabase.table("messages") \
                .select("content, is_user") \
                .eq("conversation_id", conversation_id) \
                .order("timestamp", desc=False) \
                .limit(10) \
                .execute()

            if history_result.data:
                # Formater l'historique pour le RAG agent
                for msg in history_result.data:
                    conversation_history.append({
                        "role": "user" if msg["is_user"] else "assistant",
                        "content": msg["content"]
                    })
        except Exception as e:
            # Si la récupération échoue, continuer sans historique
            # Ne pas bloquer la requête pour un échec d'historique
            print(f"Warning: Could not retrieve conversation history: {e}")
            conversation_history = []

    # Get AI response using NotariaCore RAG system
    try:
        # L'appel retourne maintenant un dictionnaire avec answer et citations
        # PROTOCOLE DAN v5 : Passer l'historique conversationnel
        ai_result = await rag_service.query(request.message, conversation_history=conversation_history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating AI response: {str(e)}")

    # Save AI response message with citations
    ai_message_id = str(uuid.uuid4())
    citations_data = ai_result.get('citations', [])
    ai_message_data = {
        "id": ai_message_id,
        "conversation_id": conversation_id,
        "content": ai_result['answer'],
        "is_user": False,
        "timestamp": datetime.utcnow().isoformat(),
        "citations": citations_data  # On passe la liste de dicts directement
    }

    try:
        result = supabase.table("messages").insert(ai_message_data).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to save AI response")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving AI response: {str(e)}")

    # Convertir les citations en objets Citation pour la réponse API (pas pour la DB)
    citations = [Citation(**citation) for citation in citations_data]

    return ChatResponse(
        response=ai_result['answer'],
        conversation_id=conversation_id,
        message_id=ai_message_id,
        citations=citations
    )
