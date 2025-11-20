from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator
from typing import List, Optional, Any, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from ..core.database import get_supabase_client
from ..api.auth import get_current_user_from_token
from ..models.schemas import UserResponse

router = APIRouter(prefix="/evaluations", tags=["evaluations"])

class EvaluationCreate(BaseModel):
    conversation_id: str
    message_id: str
    evaluation_type: str  # 'positive' or 'negative'
    comment: Optional[str] = None
    
    @validator('evaluation_type')
    def validate_evaluation_type(cls, v: str) -> str:
        if v not in ['positive', 'negative']:
            raise ValueError('evaluation_type must be "positive" or "negative"')
        return v
    
    @validator('comment', always=True)
    def validate_comment_for_negative(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        if values.get('evaluation_type') == 'negative':
            if not v or not v.strip():
                raise ValueError('comment is required for negative evaluations')
        return v

class EvaluationUpdate(BaseModel):
    evaluation_type: str
    comment: Optional[str] = None
    
    @validator('evaluation_type')
    def validate_evaluation_type(cls, v: str) -> str:
        if v not in ['positive', 'negative']:
            raise ValueError('evaluation_type must be "positive" or "negative"')
        return v
    
    @validator('comment', always=True)
    def validate_comment_for_negative(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        if values.get('evaluation_type') == 'negative':
            if not v or not v.strip():
                raise ValueError('comment is required for negative evaluations')
        return v

class EvaluationResponse(BaseModel):
    id: str
    conversation_id: str
    message_id: str
    user_id: str
    # Keep API stable: expose evaluation_type while DB column is 'feedback'
    evaluation_type: str
    comment: Optional[str]
    created_at: str
    updated_at: str

def _row_to_response(row: Dict[str, Any]) -> EvaluationResponse:
    """Normalize DB row (with 'feedback') to API response (with 'evaluation_type')."""
    normalized: Dict[str, Any] = dict(row)
    if 'evaluation_type' not in normalized and 'feedback' in normalized:
        normalized['evaluation_type'] = normalized['feedback']
    return EvaluationResponse(**normalized)

@router.post("/", response_model=EvaluationResponse)
async def create_evaluation(
    evaluation: EvaluationCreate,
    current_user: UserResponse = Depends(get_current_user_from_token),
    supabase: Any = Depends(get_supabase_client)
) -> EvaluationResponse:
    """Create a new evaluation for a chat message"""
    try:
        # Check if evaluation already exists for this message and user
        existing_result = supabase.table("evaluations").select("*").eq(
            "message_id", evaluation.message_id
        ).eq("user_id", current_user.id).execute()
        
        if existing_result.data:
            raise HTTPException(
                status_code=409, 
                detail="You have already evaluated this message. Use PUT to update your evaluation."
            )
        
        # Verify conversation exists and user has access
        conv_result = supabase.table("conversations").select("id, user_id").eq(
            "id", evaluation.conversation_id
        ).execute()
        
        if not conv_result.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conv_result.data[0]["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this conversation")
        
        # Get the question and response from messages table
        # Get the user's question (last user message in conversation)
        user_msg_result = supabase.table("messages").select("content").eq(
            "conversation_id", evaluation.conversation_id
        ).eq("is_user", True).order("timestamp", desc=True).limit(1).execute()
        
        # Get the AI response being evaluated
        ai_msg_result = supabase.table("messages").select("content, citations").eq(
            "id", evaluation.message_id
        ).execute()
        
        question = user_msg_result.data[0]["content"] if user_msg_result.data else None
        response = ai_msg_result.data[0]["content"] if ai_msg_result.data else None
        sources = ai_msg_result.data[0].get("citations", []) if ai_msg_result.data else []
        
        # Create the evaluation with new fields
        eval_data = {
            "conversation_id": evaluation.conversation_id,
            "message_id": evaluation.message_id,
            "user_id": current_user.id,
            "feedback": evaluation.evaluation_type,  # Using 'feedback' as per migration
            "comment": evaluation.comment.strip() if evaluation.comment else None,
            "question": question,
            "response": response,
            "sources": sources,
            "processed": False  # New evaluations start as unprocessed
        }
        
        result = supabase.table("evaluations").insert(eval_data).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create evaluation")
        
        return _row_to_response(result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/{evaluation_id}", response_model=EvaluationResponse)
async def update_evaluation(
    evaluation_id: str,
    evaluation: EvaluationUpdate,
    current_user: UserResponse = Depends(get_current_user_from_token),
    supabase: Any = Depends(get_supabase_client)
) -> EvaluationResponse:
    """Update an existing evaluation"""
    try:
        # Check if evaluation exists and user owns it
        existing_result = supabase.table("evaluations").select("*").eq(
            "id", evaluation_id
        ).eq("user_id", current_user.id).execute()
        
        if not existing_result.data:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        # Update the evaluation
        update_data = {
            # DB column is 'feedback'
            "feedback": evaluation.evaluation_type,
            "comment": evaluation.comment.strip() if evaluation.comment else None,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("evaluations").update(update_data).eq(
            "id", evaluation_id
        ).eq("user_id", current_user.id).execute()
        
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to update evaluation")
        
        return _row_to_response(result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/message/{message_id}", response_model=Optional[EvaluationResponse])
async def get_message_evaluation(
    message_id: str,
    current_user: UserResponse = Depends(get_current_user_from_token),
    supabase: Any = Depends(get_supabase_client)
) -> Optional[EvaluationResponse]:
    """Get the user's evaluation for a specific message"""
    try:
        result = supabase.table("evaluations").select("*").eq(
            "message_id", message_id
        ).eq("user_id", current_user.id).execute()
        
        if not result.data:
            return None
        
        return _row_to_response(result.data[0])
        
    except Exception as e:
        logger.error(f"Error getting message evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/conversation/{conversation_id}", response_model=List[EvaluationResponse])
async def get_conversation_evaluations(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_user_from_token),
    supabase: Any = Depends(get_supabase_client)
) -> List[EvaluationResponse]:
    """Get all evaluations for a conversation (user's own evaluations only)"""
    try:
        # Verify user has access to this conversation
        conv_result = supabase.table("conversations").select("user_id").eq(
            "id", conversation_id
        ).execute()
        
        if not conv_result.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conv_result.data[0]["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied to this conversation")
        
        # Get evaluations
        result = supabase.table("evaluations").select("*").eq(
            "conversation_id", conversation_id
        ).eq("user_id", current_user.id).order("created_at", desc=True).execute()
        
        return [EvaluationResponse(**eval_data) for eval_data in result.data] if result.data else []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation evaluations: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/stats/summary")
async def get_evaluation_stats(
    current_user: UserResponse = Depends(get_current_user_from_token),
    supabase: Any = Depends(get_supabase_client)
) -> Dict[str, Any]:
    """Get evaluation statistics for the current user"""
    try:
        # Get user's evaluation statistics
        # Table now stores 'feedback'; select that and compute stats accordingly
        result = supabase.table("evaluations").select("feedback").eq(
            "user_id", current_user.id
        ).execute()
        
        stats = {
            "total_evaluations": 0,
            "positive_evaluations": 0,
            "negative_evaluations": 0,
            "positive_percentage": 0.0
        }
        
        if result.data:
            stats["total_evaluations"] = len(result.data)
            stats["positive_evaluations"] = len([e for e in result.data if e.get("feedback") == "positive"])
            stats["negative_evaluations"] = len([e for e in result.data if e.get("feedback") == "negative"])
            
            if stats["total_evaluations"] > 0:
                stats["positive_percentage"] = round(
                    (stats["positive_evaluations"] / stats["total_evaluations"]) * 100, 2
                )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting evaluation stats: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/{evaluation_id}")
async def delete_evaluation(
    evaluation_id: str,
    current_user: UserResponse = Depends(get_current_user_from_token),
    supabase: Any = Depends(get_supabase_client)
) -> Dict[str, str]:
    """Delete an evaluation"""
    try:
        # Check if evaluation exists and user owns it
        existing_result = supabase.table("evaluations").select("id").eq(
            "id", evaluation_id
        ).eq("user_id", current_user.id).execute()
        
        if not existing_result.data:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        # Delete the evaluation
        result = supabase.table("evaluations").delete().eq(
            "id", evaluation_id
        ).eq("user_id", current_user.id).execute()
        
        return {"message": "Evaluation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
