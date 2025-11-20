from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from typing import Dict, Any, MutableMapping

from .api import documents, conversations, chat, auth, evaluations, admin
from .routes import embedding
from .core.config import settings
from .core.database import init_db, get_supabase_client
from .core.logger import logger
from .services.minio_service import get_minio_service
from .services.neo4j_service import get_neo4j_service
from .services.notaria_rag_service import get_rag_service
from .api.auth import get_current_user_from_token
from .models.schemas import ChatRequest, ChatResponse, UserResponse
from fastapi import Depends

# Load environment variables
load_dotenv()

app = FastAPI(
    title="MarIAnne Backend",
    description="Self-hosted AI chatbot backend with document processing",
    version="1.0.0",
    redirect_slashes=False  # Disable automatic trailing slash redirects
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9002", "http://frontend:9002", "http://localhost:3000", "http://frontend:3000", "https://chat.chatbotpro.fr", "http://api.chatbotpro.fr", "https://api.chatbotpro.fr"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware for debugging CORS issues
@app.middleware("http")
async def log_requests(request: Any, call_next: Any) -> Any:
    # Log all incoming requests
    logger.debug(f"Request - Method: {request.method}, URL: {request.url}, Origin: {request.headers.get('origin')}")

    # Handle OPTIONS requests specifically
    if request.method == "OPTIONS":
        logger.debug(f"PREFLIGHT REQUEST - Origin: {request.headers.get('origin')}, URL: {request.url}")

    # Log request body for POST requests to /api/chat
    if request.method == "POST" and "/api/chat" in str(request.url):
        try:
            body = await request.body()
            logger.debug(f"POST BODY to /api/chat: {body.decode('utf-8')}")
        except Exception as e:
            logger.error(f"Could not read body: {e}")

    try:
        response = await call_next(request)
        logger.debug(f"Response - Status: {response.status_code}")
        return response
    except Exception as e:
        logger.exception(f"Request failed: {e}")
        raise


# Mount static files for document uploads (use local dir for development)
upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

# Include API routes
app.include_router(auth.router, prefix="/api", tags=["authentication"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(conversations.router, prefix="/api", tags=["conversations"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(evaluations.router, prefix="/api", tags=["evaluations"])
app.include_router(embedding.router, prefix="/api", tags=["embedding"])
app.include_router(admin.router, tags=["admin"])


@app.on_event("startup")
async def startup() -> None:
    """Initialize database and services on startup"""
    logger.info("Starting backend services...")

    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    try:
        # Initialize Minio service
        minio_service = get_minio_service()
        await minio_service.initialize()
        logger.info("MinIO service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MinIO: {e}")
        raise

    try:
        # Initialize Neo4j service
        neo4j_service = get_neo4j_service()
        await neo4j_service.initialize()
        logger.info("Neo4j service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j: {e}")
        raise

    try:
        # Initialize NotariaCore service
        notaria_core = get_rag_service()
        logger.info("RAG service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {e}")
        raise

    logger.success("✅ Backend started successfully (connected to Supabase, Minio, Neo4j)")

@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "ChatDocAI Backend API", "version": "1.0.0"}

@app.get("/test")
async def test() -> Dict[str, str]:
    return {"message": "Backend is working", "timestamp": "2025-01-01T00:00:00Z"}

@app.get("/debug-supabase")
async def debug_supabase() -> Dict[str, Any]:
    from .core.database import get_supabase
    from .core.config import settings

    return {
        "supabase_url": settings.supabase_url,
        "supabase_key_prefix": settings.supabase_key[:20] + "...",
        "client_exists": get_supabase() is not None
    }

@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint with real connectivity tests"""
    from .core.database import get_supabase

    health_status: Dict[str, Any] = {"status": "healthy", "services": {}}

    # Test Supabase connection
    try:
        supabase = get_supabase()
        if supabase:
            result = supabase.table("users").select("count").execute()
            health_status["services"]["supabase"] = "connected"
            logger.debug("Supabase health check: OK")
    except Exception as e:
        health_status["services"]["supabase"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"Supabase health check failed: {e}")

    # Test Neo4j connection
    try:
        neo4j_service = get_neo4j_service()
        # Ensure driver is initialized
        if neo4j_service.driver is None:
            await neo4j_service.initialize()
        if neo4j_service.driver:
            async with neo4j_service.driver.session() as session:
                result = await session.run("RETURN 1 as test")
                await result.single()
        health_status["services"]["neo4j"] = "connected"
        logger.debug("Neo4j health check: OK")
    except Exception as e:
        health_status["services"]["neo4j"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"Neo4j health check failed: {e}")

    # Test MinIO connection
    try:
        minio_service = get_minio_service()
        # Ensure client is initialized
        if minio_service.client is None:
            await minio_service.initialize()
        client = minio_service.client
        assert client is not None
        # List buckets to test connection
        _ = client.list_buckets()
        health_status["services"]["minio"] = "connected"
        logger.debug("MinIO health check: OK")
    except Exception as e:
        health_status["services"]["minio"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"MinIO health check failed: {e}")

    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
