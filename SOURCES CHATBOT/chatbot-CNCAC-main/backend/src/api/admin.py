"""
Admin API endpoints for evaluation management and validation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..core.database import get_supabase
from ..services.neo4j_service import Neo4jService
from ..api.auth import get_current_user_from_token
from ..models.schemas import UserResponse

logger = logging.getLogger(__name__)


async def require_admin(current_user: UserResponse = Depends(get_current_user_from_token)) -> UserResponse:
    """
    Middleware to ensure user has admin role
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Accès administrateur requis"
        )
    return current_user


router = APIRouter(
    prefix="/api/admin", 
    tags=["admin"],
    dependencies=[Depends(require_admin)]
)


@router.get("/evaluations/pending")
async def get_pending_evaluations() -> Dict[str, Any]:
    """
    Get all negative evaluations that haven't been processed yet
    """
    try:
        # Fetch negative evaluations that haven't been processed
        db = get_supabase()
        result = db.table("evaluations") \
            .select("*") \
            .eq("feedback", "negative") \
            .eq("processed", False) \
            .order("created_at", desc=False) \
            .execute()
        
        evaluations = result.data if result.data else []
        
        logger.info(f"Admin retrieved {len(evaluations)} pending evaluations")
        return {"evaluations": evaluations}
        
    except Exception as e:
        logger.error(f"Error fetching pending evaluations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pending evaluations: {str(e)}"
        )


@router.post("/evaluations/{evaluation_id}/approve")
async def approve_evaluation(
    evaluation_id: str,
    current_user: UserResponse = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    Approve evaluation and apply corrections to the knowledge graph
    """
    try:
        # Get evaluation details
        db = get_supabase()
        evaluation_result = db.table("evaluations") \
            .select("*") \
            .eq("id", evaluation_id) \
            .single() \
            .execute()
        
        if not evaluation_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation {evaluation_id} not found"
            )
        
        evaluation = evaluation_result.data
        
        # Check if already processed
        if evaluation.get("processed", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evaluation already processed"
            )
        
        # Update evaluation as processed
        update_result = db.table("evaluations") \
            .update({
                "processed": True,
                "processed_by": current_user.id,
                "processed_at": datetime.utcnow().isoformat()
            }) \
            .eq("id", evaluation_id) \
            .execute()
        
        # Apply corrections to Neo4j if comment contains correction info
        if evaluation.get("comment") and evaluation["feedback"] == "negative":
            neo4j_service = Neo4jService()
            
            try:
                await neo4j_service.initialize()
                
                # Get message details to identify affected chunks
                message_result = db.table("messages") \
                    .select("*") \
                    .eq("id", evaluation["message_id"]) \
                    .single() \
                    .execute()
                
                if message_result.data:
                    message = message_result.data
                    
                    # Extract chunk IDs from citations if available
                    citations = message.get("citations", [])
                    
                    if citations:
                        # Reduce reliability of misleading chunks based on document sources
                        for citation in citations:
                            try:
                                # Find chunks from the cited document
                                query = """
                                MATCH (d:Document {id: $doc_id})-[:CONTAINS]->(c:Chunk)
                                SET c.reliability = COALESCE(c.reliability, 1.0) * 0.9,
                                    c.last_corrected = datetime(),
                                    c.correction_count = COALESCE(c.correction_count, 0) + 1
                                RETURN COUNT(c) as chunks_updated
                                """
                                if neo4j_service.driver:
                                    async with neo4j_service.driver.session() as session:
                                        result = await session.run(query, {"doc_id": citation.get("documentId")})
                                        record = await result.single()
                                        if record:
                                            logger.info(
                                                f"Reduced reliability for {record['chunks_updated']} chunks from document {citation.get('documentId')}"
                                            )
                            except Exception as chunk_error:
                                logger.warning(f"Failed to update chunks for document {citation.get('documentId')}: {str(chunk_error)}")
                    
                    # Store the negative feedback as a learning example
                    try:
                        query = """
                        CREATE (l:LearningExample {
                            id: randomUUID(),
                            evaluation_id: $evaluation_id,
                            original_query: $query,
                            original_response: $original_response,
                            user_comment: $user_comment,
                            feedback_type: 'negative',
                            approved_by: $admin_id,
                            approved_at: datetime(),
                            created_at: datetime()
                        })
                        RETURN l.id as learning_id
                        """
                        if neo4j_service.driver:
                            async with neo4j_service.driver.session() as session:
                                result = await session.run(
                                    query,
                                    {
                                        "evaluation_id": evaluation_id,
                                        "query": evaluation.get("question", ""),
                                        "original_response": evaluation.get("response", ""),
                                        "user_comment": evaluation.get("comment", ""),
                                        "admin_id": current_user.id
                                    }
                                )
                                record = await result.single()
                                if record:
                                    logger.info(f"Created learning example {record['learning_id']}")
                    except Exception as learning_error:
                        logger.warning(f"Failed to create learning example: {str(learning_error)}")
                
            except Exception as neo4j_error:
                logger.error(f"Error applying corrections to Neo4j: {str(neo4j_error)}")
                # Don't fail the approval, just log the error
            finally:
                await neo4j_service.close()
        
        logger.info(f"Admin {current_user.id} approved evaluation {evaluation_id}")
        
        return {
            "status": "success",
            "message": f"Evaluation {evaluation_id} approved and corrections applied",
            "evaluation_id": evaluation_id,
            "reviewed_by": current_user.id,
            "reviewed_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving evaluation {evaluation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve evaluation: {str(e)}"
        )


@router.post("/evaluations/{evaluation_id}/reject")
async def reject_evaluation(
    evaluation_id: str,
    rejection_reason: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user_from_token)
) -> Dict[str, Any]:
    """
    Reject evaluation without applying corrections
    """
    try:
        # Get evaluation details
        db = get_supabase()
        evaluation_result = db.table("evaluations") \
            .select("*") \
            .eq("id", evaluation_id) \
            .single() \
            .execute()
        
        if not evaluation_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluation {evaluation_id} not found"
            )
        
        evaluation = evaluation_result.data
        
        # Check if already processed
        if evaluation.get("processed", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evaluation already processed"
            )
        
        # Update evaluation as processed but rejected
        update_data = {
            "processed": True,
            "processed_by": current_user.id,
            "processed_at": datetime.utcnow().isoformat(),
            "rejected": True
        }
        
        if rejection_reason:
            update_data["rejection_reason"] = rejection_reason
        
        update_result = db.table("evaluations") \
            .update(update_data) \
            .eq("id", evaluation_id) \
            .execute()
        
        # Optionally store rejection in Neo4j for learning
        neo4j_service = Neo4jService()
        try:
            await neo4j_service.initialize()
            
            query = """
            CREATE (r:RejectedEvaluation {
                id: randomUUID(),
                evaluation_id: $evaluation_id,
                reason: $reason,
                rejected_by: $admin_id,
                rejected_at: datetime(),
                created_at: datetime()
            })
            RETURN r.id as rejection_id
            """
            if neo4j_service.driver:
                async with neo4j_service.driver.session() as session:
                    result = await session.run(
                        query,
                        {
                            "evaluation_id": evaluation_id,
                            "reason": rejection_reason or "No reason provided",
                            "admin_id": current_user.id
                        }
                    )
                    record = await result.single()
                    if record:
                        logger.info(f"Stored rejection record {record['rejection_id']}")
        except Exception as neo4j_error:
            logger.warning(f"Failed to store rejection in Neo4j: {str(neo4j_error)}")
        finally:
            await neo4j_service.close()
        
        logger.info(f"Admin {current_user.id} rejected evaluation {evaluation_id}")
        
        return {
            "status": "success",
            "message": f"Evaluation {evaluation_id} rejected",
            "evaluation_id": evaluation_id,
            "reviewed_by": current_user.id,
            "reviewed_at": datetime.utcnow().isoformat(),
            "rejection_reason": rejection_reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting evaluation {evaluation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject evaluation: {str(e)}"
        )


@router.get("/stats")
async def get_admin_stats() -> Dict[str, Any]:
    """
    Get admin dashboard statistics
    """
    try:
        # Get evaluation statistics
        db = get_supabase()
        
        # Count pending negative evaluations
        pending_count = db.table("evaluations") \
            .select("id", count="exact") \
            .eq("feedback", "negative") \
            .eq("processed", False) \
            .execute()
        
        # Count processed evaluations
        processed_count = db.table("evaluations") \
            .select("id", count="exact") \
            .eq("processed", True) \
            .execute()
        
        # Count positive evaluations
        positive_count = db.table("evaluations") \
            .select("id", count="exact") \
            .eq("feedback", "positive") \
            .execute()
        
        # Count negative evaluations
        negative_count = db.table("evaluations") \
            .select("id", count="exact") \
            .eq("feedback", "negative") \
            .execute()
        
        # Get graph statistics from Neo4j
        neo4j_service = Neo4jService()
        try:
            await neo4j_service.initialize()
            
            graph_stats_query = """
            MATCH (c:Chunk)
            WITH COUNT(c) as total_chunks,
                 AVG(COALESCE(c.reliability, 1.0)) as avg_reliability,
                 COUNT(CASE WHEN c.reliability < 0.5 THEN 1 END) as low_reliability_chunks
            OPTIONAL MATCH (e:Entity)
            WITH total_chunks, avg_reliability, low_reliability_chunks, 
                 COUNT(DISTINCT e) as total_entities
            OPTIONAL MATCH ()-[r]->()
            WITH total_chunks, avg_reliability, low_reliability_chunks,
                 total_entities, COUNT(DISTINCT r) as total_relations
            OPTIONAL MATCH (l:LearningExample)
            RETURN {
                chunks: {
                    total: total_chunks,
                    avg_reliability: avg_reliability,
                    low_reliability: low_reliability_chunks
                },
                entities: {
                    total: total_entities
                },
                relations: {
                    total: total_relations
                },
                learning_examples: COUNT(l)
            } as stats
            """
            if neo4j_service.driver:
                async with neo4j_service.driver.session() as session:
                    result = await session.run(graph_stats_query)
                    record = await result.single()
                    graph_stats = record["stats"] if record else {}
        except Exception as neo4j_error:
            logger.warning(f"Failed to get graph stats: {str(neo4j_error)}")
            graph_stats = {}
        finally:
            await neo4j_service.close()
        
        return {
            "evaluations": {
                "pending_negative": pending_count.count if pending_count else 0,
                "processed": processed_count.count if processed_count else 0,
                "positive": positive_count.count if positive_count else 0,
                "negative": negative_count.count if negative_count else 0,
                "total": (positive_count.count if positive_count else 0) + (negative_count.count if negative_count else 0)
            },
            "graph": graph_stats,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching admin stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch admin statistics: {str(e)}"
        )