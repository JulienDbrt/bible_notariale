# ChatDocAI - AI-Powered Document Intelligence Platform

ChatDocAI is a sophisticated self-hosted AI chatbot designed for French notaries (notaires) that enables intelligent conversations with documents using advanced RAG (Retrieval-Augmented Generation) capabilities, knowledge graphs, and multi-strategy query planning.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM
- Ports 3000 (frontend) and 8000 (backend) available
- **Remote Services Required**:
  - Neo4j database instance
  - MinIO object storage
  - Supabase PostgreSQL database
  - OpenAI API key

### Installation

```bash
# Clone repository
git clone <repository-url>
cd chatbot-CNCAC

# Setup environment using Makefile
make setup           # Creates all .env files from templates
make dev-start       # Start all services

# Or manually
cp .env.example .env
cp front/.env.local.example front/.env.local
cp backend/.env.example backend/.env
docker-compose -f docker-compose.dev.yml up -d
```

### Access Points
- **Frontend**: http://localhost:9002 (dev) / http://localhost:3000 (prod)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin123)

## 🏗️ Architecture Overview

### Tech Stack

#### Backend (FastAPI + Python 3.11)
- **Graph Database**: Neo4j for knowledge graph and vector storage (1536-dim embeddings)
- **Object Storage**: MinIO S3-compatible storage for documents
- **Database**: Supabase (PostgreSQL) for user data and metadata
- **Document Processing**: Hybrid approach with PyMuPDF (fast text) + Docling (OCR fallback)
- **RAG Engine**: Custom multi-strategy system with AI-powered query planning
- **LLM Models**: Configurable OpenAI models for different tasks
- **Testing**: Comprehensive pytest suite with coverage reporting

#### Frontend (Next.js 15 + React 18)
- **UI Framework**: Radix UI components with Tailwind CSS
- **Type Safety**: Full TypeScript implementation
- **Authentication**: Supabase Auth with backend proxy pattern
- **AI Integration**: Google Genkit with Gemini 2.0 Flash (limited use)
- **State Management**: React Context API with custom hooks
- **Features**: Real-time chat, document management, admin dashboard

## 📋 Core Features

### 1. Intelligent Document Processing Pipeline
```
Document Upload → MinIO Storage → Text Extraction → Semantic Chunking (512 tokens)
    ↓                                      ↓                    ↓
Entity Extraction ← LLM Analysis → Neo4j Graph → Vector Embeddings
```

**Supported Formats**: PDF, DOCX, TXT, MD, EML, HTML, RTF, PPT, XLS (15+ formats via Docling)

### 2. Advanced RAG System - PROTOCOLE DAN v5

**ReAct Agent Architecture** (Reason + Act + Observe) with Conversational Memory

The RAG system implements an intelligent agent that reasons about queries like a legal expert while maintaining conversational context across multiple turns.

**Architecture Phases**:
1. **REASON**: Analyzes question + conversation history, resolves coreferences, expands legal synonyms
2. **ACT**: Executes hybrid search (vector + full-text), LLM-based reranking
3. **OBSERVE**: Synthesizes context-aware response with citations

**Key Features**:
- **Conversational Memory**: Maintains context from last 10 messages
- **Semantic Gap Resolution**: Automatic synonym expansion (no manual maintenance)
- **Hybrid Search**: Parallel vector (cosine) + full-text (Lucene) retrieval
- **Intelligent Reranking**: LLM-scored relevance for optimal results
- **Coreference Resolution**: Understands implicit references ("cette négociation" → "négociation immobilière")

### 3. Knowledge Graph Features
- Automatic entity and relationship extraction
- Graph enrichment agent for transitive inferences
- Anomaly detection in relationships
- Visual graph exploration (frontend integration)

### 4. User Features
- **Real-time Chat**: Streaming responses with source citations
- **Document Management**: Upload, organize in folders, track processing status
- **Evaluation System**: Rate AI responses for continuous improvement
- **Admin Dashboard** ("Le Tribunal"): Feedback management system
- **Conversation History**: Persistent chat sessions with search

## 🔧 Configuration

### Required Environment Variables

```bash
# backend/.env
SUPABASE_URL=https://your-instance.supabase.co
SUPABASE_KEY=your_service_role_key

NEO4J_URL=bolt://your-neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

MINIO_ENDPOINT=your-minio.domain.com
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key

OPENAI_API_KEY=your_openai_key

# Optional model configuration
LLM_EXTRACTION_MODEL=gpt-4.1-mini-2025-04-14
LLM_PLANNER_MODEL=gpt-4.1-nano-2025-04-14
LLM_SYNTHESIS_MODEL=gpt-4.1-2025-04-14

# front/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-instance.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

## 📁 Project Structure

```
chatbot-CNCAC/
├── backend/
│   ├── src/
│   │   ├── api/              # FastAPI endpoints
│   │   ├── core/             # Configuration & database
│   │   ├── models/           # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   ├── neo4j_service.py
│   │   │   ├── minio_service.py
│   │   │   └── notaria_rag_service.py
│   │   └── agents/           # Autonomous agents
│   ├── scripts/
│   │   └── ingestion_pipeline.py  # Document processing
│   └── tests/                # Comprehensive test suite
├── front/
│   ├── src/
│   │   ├── app/              # Next.js App Router
│   │   ├── components/       # React components
│   │   │   └── ui/          # Radix UI primitives
│   │   ├── lib/             # Utilities & API client
│   │   ├── contexts/        # React contexts
│   │   └── ai/              # Genkit configuration
│   └── package.json
├── docker-compose.yml        # Production config
├── docker-compose.dev.yml    # Development config
└── Makefile                  # Development commands
```

## 🧪 Testing

### Backend Testing

#### Installation
```bash
cd backend
# Install with test dependencies (modern approach via pyproject.toml)
pip install -e ".[test]"

# Or install all development dependencies
pip install -e ".[dev]"
```

#### Running Tests
```bash
pytest                        # Run all tests
pytest --cov                  # With coverage report
pytest tests/test_api.py      # Specific test file
pytest -m unit               # Run only unit tests
pytest -m integration        # Run only integration tests
```

**Test Coverage**: Comprehensive suite covering:
- API endpoints
- Neo4j operations
- RAG service strategies
- Document processing
- Authentication flows
- Coverage threshold: 70% minimum

### Frontend Testing
```bash
cd front
npm test                      # Run tests with Jest
npm run test:watch           # Watch mode
npm run test:coverage        # Coverage report
npm run lint                  # ESLint
npm run typecheck            # TypeScript checking
```

**Note**: Frontend test infrastructure is configured but tests need to be implemented.

## 🚀 Development

### Development Commands
```bash
# Using Makefile
make dev-start               # Start all services
make dev-logs               # View logs
make dev-stop               # Stop services
make rebuild-backend        # Rebuild backend
make rebuild-frontend       # Rebuild frontend

# Backend development
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development
cd front
npm run dev                 # Start dev server (port 9002 with Turbopack)
npm run build              # Production build
```

### Document Ingestion
```bash
# Process documents
cd backend
python scripts/ingestion_pipeline.py           # Single batch
python scripts/ingestion_pipeline.py --daemon  # Continuous monitoring

# Graph enrichment
python -m src.agents.graph_enrichment_agent
```

## 🔒 Security 

### Security Features
- **Authentication**: JWT-based authentication with proper token validation
- **Authorization**: User-scoped access control for all resources
- **Input Validation**: Parameterized queries prevent injection attacks
- **File Upload Security**: MIME type validation and content scanning
- **CORS Configuration**: Properly restricted to trusted origins only
- **Environment Security**: All sensitive configuration externalized

### Best Practices
- Rotate API keys regularly
- Use `.env.example` files as templates
- Enable Supabase RLS (Row Level Security)
- Implement rate limiting for production
- Regular security audits and dependency updates

## 📊 Performance Characteristics

- **Document Processing**: ~2-5 pages/second (with OCR)
- **Embedding Generation**: Batch processing (100 chunks)
- **RAG Query Latency**: <2s average
- **Graph Traversal**: Limited to 2 hops
- **Query Planning**: <200ms with LLM
- **Concurrent Operations**: 2 documents simultaneously

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests before committing
4. Follow existing code patterns
5. Update documentation as needed

## 📄 License

[Add your license here]

## 🆘 Support

For issues and questions:
- Check API documentation at `/docs`
- Review error logs with `make dev-logs`
- Open an issue on GitHub

---

**Note**: This is an active development project. Some features may be experimental or subject to change.