# ChatDocAI - Quick Reference Guide

## Project Overview
- **Name**: ChatDocAI (MarIAnne Backend)
- **Purpose**: Self-hosted AI chatbot for French notaries with RAG capabilities
- **Current Status**: Active development on `rag-bugfix` branch
- **Test Status**: 100% pass rate (20/20 core tests), 60/60 passing

## Repository Structure

```
chatbot-CNCAC/
├── backend/              FastAPI + Python 3.11+
│   ├── src/api/         6 REST API routers
│   ├── src/services/    4 core services (NotariaRAG, Neo4j, MinIO, Ontology)
│   ├── src/agents/      Graph enrichment agent
│   ├── scripts/         CLI utilities
│   └── tests/          16 test modules
├── front/              Next.js 15 + React 18 + TypeScript
│   ├── src/app/        Page routes (auth, app)
│   ├── src/components/ 50+ React components
│   └── src/lib/        API client, types, utilities
└── supabase/           Database migrations
```

## Key Files & Line Counts

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| **RAG Core** | notaria_rag_service.py | 1,079 | PROTOCOLE DAN v5 (Reason→Act→Observe) |
| **Graph DB** | neo4j_service.py | 565 | Knowledge graph + vector search |
| **Main** | main.py | 199 | FastAPI app setup |
| **Config** | config.py | 92 | Environment variables & settings |
| **Storage** | minio_service.py | 164 | S3-compatible file storage |
| **Tests** | 16 modules | 1,000+ | Comprehensive pytest suite |

## Technology Stack

### Backend
```
FastAPI 0.115.6        Web framework
Neo4j 5.26.0           Knowledge graph + vectors
Supabase 2.3.0         PostgreSQL + Auth
MinIO 7.2.12           S3-compatible storage
Docling 2.14.0         Document parsing (OCR fallback)
PyMuPDF 1.26.3         Fast PDF extraction
OpenAI 1.58.1          Embeddings + LLM
```

### Frontend
```
Next.js 15.5.0         React framework + App Router
React 18.3.1           UI library
TypeScript 5.7.3       Type safety (strict)
Radix UI               Component primitives
Tailwind CSS 3.4.1     Styling
React Hook Form 7.54.2 Form management
Zod 3.24.2             Runtime validation
Google Genkit 1.14.1   AI integration
```

### Infrastructure
```
Docker Compose         Container orchestration
Makefile               Development commands
GitHub Actions         CI/CD
pytest                 Testing framework (Python)
Jest                   Testing framework (JavaScript)
```

## API Endpoints

```
POST   /api/auth/signup              User registration
POST   /api/auth/login               User login
POST   /api/auth/logout              User logout
GET    /api/auth/me                  Get current user

POST   /api/documents/upload         Upload file
GET    /api/documents/               List documents
GET    /api/documents/{id}           Get document details
DELETE /api/documents/{id}           Delete document
POST   /api/documents/start_ingestion Trigger processing

POST   /api/chat                     Send chat message
GET    /api/conversations/           List conversations
GET    /api/conversations/{id}       Get conversation
DELETE /api/conversations/{id}       Delete conversation

POST   /api/evaluations/             Submit feedback
GET    /api/evaluations/             List evaluations

GET    /api/admin/evaluations        Admin dashboard
```

## Environment Configuration

### Backend (.env)
```
SUPABASE_URL           PostgreSQL remote instance
SUPABASE_KEY           Service role key
NEO4J_URL              Graph DB bolt connection
NEO4J_USERNAME         Graph DB user
NEO4J_PASSWORD         Graph DB password
MINIO_ENDPOINT         S3 storage endpoint
MINIO_ROOT_USER        S3 access key
MINIO_ROOT_PASSWORD    S3 secret key
OPENAI_API_KEY         Embeddings & LLM API
EMBEDDING_MODEL        text-embedding-3-small (default)
EMBEDDING_DIMENSIONS   1536 (default)
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL           Backend API URL
NEXT_PUBLIC_SUPABASE_URL      Supabase endpoint
NEXT_PUBLIC_SUPABASE_ANON_KEY Anon key for auth
```

## Common Commands

### Setup & Deployment
```bash
make setup              # Initialize .env files
make dev-start          # Start development services
make dev-stop           # Stop services
make rebuild-backend    # Rebuild backend only
make rebuild-frontend   # Rebuild frontend only
```

### Testing
```bash
make test               # Run all tests
make test-backend       # Backend tests with coverage
pytest                  # Run tests manually
pytest --cov           # With coverage report
```

### Code Quality
```bash
make lint              # Lint all code
make format            # Format code
make typecheck         # Type checking
make pre-commit        # Full CI locally
```

### Backend Development
```bash
cd backend
pip install -e ".[dev]"                    # Install with dev deps
uvicorn src.main:app --reload              # Run server
python scripts/ingestion_pipeline.py       # Process documents
python -m src.agents.graph_enrichment_agent # Enrich graph
```

### Frontend Development
```bash
cd front
npm install
npm run dev            # Start dev server (port 9002)
npm run build          # Production build
npm run lint           # ESLint
npm run typecheck      # TypeScript check
```

## Data Flow

### Chat Interaction (PROTOCOLE DAN v5)
```
User Message
  ↓
POST /api/chat
  ↓
Backend saves message to Supabase
  ↓
RAG Service
  ├─ REASON: Analyze query + history, expand synonyms
  ├─ ACT: Vector search + Full-text search + Rerank
  └─ OBSERVE: Generate response + Extract citations
  ↓
Save response to Supabase
  ↓
Return ChatResponse with citations
  ↓
Frontend displays with source tooltips
```

### Document Processing
```
Upload Document
  ↓
POST /api/documents/upload
  ↓
Save to MinIO (S3-compatible)
  ↓
Start ingestion pipeline
  ↓
Extract text (PyMuPDF or Docling)
  ↓
Semantic chunking (512 tokens)
  ↓
Entity extraction (LLM)
  ↓
Vector embedding (OpenAI)
  ↓
Store in Neo4j (graph + vectors)
  ↓
Update status in Supabase
```

## RAG System Architecture

### PROTOCOLE DAN v5 (ReAct: Reason → Act → Observe)

**REASON Phase** (gpt-4.1-nano)
- Analyze user question + conversation history (10 messages)
- Resolve coreferences ("cette négociation" → full term)
- Expand legal synonyms automatically
- Formulate optimized search query

**ACT Phase** (Parallel execution)
- **Vector Search**: Cosine similarity on 1536-dim embeddings
- **Full-Text Search**: Lucene index on chunk text
- **Merge & Deduplicate**: Combine results
- **Rerank**: LLM scores relevance

**OBSERVE Phase** (gpt-4.1-2025)
- Generate response using top-K chunks
- Maintain conversational context
- Extract citations automatically
- Return source attribution

## Graph Model

```
Document (user's file)
  ├─ contains → Chunk (512 tokens)
  │           ├─ has_embedding → Vector[1536]
  │           └─ extracted_entity → Entity
  │
  └─ Entity (Person, Org, Location, Contract, Article)
      ├─ works_for → Organization
      ├─ located_at → Location
      ├─ references → Legal Article
      └─ related_to → Entity (inferred)
```

## Deployment Ports

```
Frontend (Dev)    : http://localhost:9002 (Turbopack)
Frontend (Prod)   : http://localhost:3000
Backend API       : http://localhost:8000
API Docs (Swagger): http://localhost:8000/docs
MinIO Console     : http://localhost:9001
Supabase          : http://localhost:54321
```

## Code Quality Standards

### Backend
- **Type Checking**: Strict mypy (all 137 errors fixed)
- **Linting**: Ruff (100 char lines, double quotes)
- **Testing**: pytest with 70% coverage target
- **Async**: All I/O operations are async

### Frontend
- **Type Checking**: Strict TypeScript (no implicit any)
- **Linting**: ESLint + Next.js plugin
- **Testing**: Jest + React Testing Library
- **Styling**: Tailwind CSS utilities

## Testing Status

```
✅ Core Tests:      60/60 passing (100% pass rate)
✅ Config Tests:    Passing
✅ Database Tests:  Passing
✅ MinIO Tests:     Passing
⚠️  Coverage:        28-30% (target: 70%)
⚠️  Needs Work:      RAG service integration tests
```

## Recent Activity

**Branch**: rag-bugfix
**Modified Files**: 9 (docs, config, services)
**Recent Commits**:
1. Fix npm audit vulnerabilities (security)
2. Fix all failing tests (100% pass rate)
3. Neo4j traversal + PROTOCOLE DAN optimizations

## Key Design Patterns

### Backend
- **Singleton Pattern**: Services initialized once
- **Dependency Injection**: FastAPI Depends()
- **Async/Await**: All I/O operations
- **Layered Architecture**: Routes → Services → Core → External

### Frontend
- **App Router**: Next.js file-based routing
- **React Context**: AuthContext for state
- **Component Composition**: Radix UI + custom components
- **Type Safety**: Full TypeScript + Zod validation

## Quick Debugging

### Health Check
```bash
curl http://localhost:8000/health
```

### View Logs
```bash
make dev-logs           # All services
make logs-backend       # Backend only
docker-compose logs -f backend
```

### Access Services
```bash
make backend            # Backend shell
make frontend           # Frontend shell
make database           # Database shell
```

### Test Specific Module
```bash
pytest tests/test_neo4j_service.py -v
pytest -k "test_upload" -v
```

## Important Notes

1. **Remote Services**: Neo4j, MinIO, Supabase are remote - not containerized locally
2. **Never commit .env files** with secrets
3. **Always run tests before commit**: `make pre-commit`
4. **Documentation**: Keep ARCHITECTURE.md, CLAUDE.md in sync
5. **Git workflow**: Create feature branches from dev, PR to main
6. **Type safety**: Run `mypy src/` before deployment
7. **Coverage**: Aim for 70%+ test coverage

## Useful Resources

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ARCHITECTURE.md**: Detailed system architecture (390+ lines)
- **CLAUDE.md**: Project guidelines and instructions
- **README.md**: Quick start guide
- **CODEBASE_ANALYSIS.md**: Comprehensive codebase overview (1000+ lines)

---

Last Updated: October 25, 2025
Current Status: Active Development
Branch: rag-bugfix
