# ChatDocAI Repository - Comprehensive Structural Analysis

## Executive Summary

ChatDocAI is a sophisticated self-hosted AI chatbot platform designed for French notaries, implementing an advanced **Retrieval-Augmented Generation (RAG)** system with Neo4j knowledge graphs, vector search, and intelligent query planning. The project uses a modern full-stack architecture with FastAPI backend (Python 3.11+) and Next.js 15 frontend (React 18 + TypeScript).

**Current Status**: Active development on `rag-bugfix` branch with 9 modified files and recent test fixes achieving 100% pass rate.

---

## 1. DIRECTORY STRUCTURE OVERVIEW

```
chatbot-CNCAC/
├── backend/                          # Python FastAPI backend (1883 lines core services)
│   ├── src/                          # Application source code
│   │   ├── api/                      # REST API endpoints (6 routes)
│   │   ├── core/                     # Core configuration & services
│   │   ├── agents/                   # Autonomous agents (graph enrichment)
│   │   ├── models/                   # Pydantic schemas
│   │   ├── routes/                   # Additional routes (embedding)
│   │   ├── services/                 # Business logic (4 major services)
│   │   ├── prompts/                  # LLM prompt templates
│   │   └── main.py                   # FastAPI application entry point
│   ├── scripts/                      # CLI utilities (4 scripts)
│   ├── tests/                        # Comprehensive test suite (16 test modules)
│   ├── migrations/                   # Database migrations
│   ├── ontologies/                   # OWL ontology definitions
│   ├── pyproject.toml                # Modern Python packaging (PEP 621)
│   └── pytest.ini                    # Test configuration
│
├── front/                            # Next.js 15 frontend
│   ├── src/
│   │   ├── app/                      # Next.js App Router pages
│   │   │   ├── (auth)/               # Authentication routes
│   │   │   └── (app)/                # Main application routes
│   │   ├── components/               # React components (50+ UI + custom)
│   │   ├── contexts/                 # React Context for state
│   │   ├── hooks/                    # Custom React hooks
│   │   ├── lib/                      # Utilities & API client
│   │   └── ai/                       # Google Genkit integration
│   ├── package.json                  # npm dependencies & scripts
│   ├── next.config.ts                # Next.js configuration
│   └── tailwind.config.ts            # Tailwind CSS configuration
│
├── supabase/                         # Database migrations
│   └── migrations/                   # PostgreSQL schema definitions
│
├── docs/                             # Documentation files
├── scripts/                          # Root-level utility scripts
├── Makefile                          # Development command shortcuts
├── docker-compose.dev.yml            # Development environment
├── docker-compose.yml                # Production environment
├── ARCHITECTURE.md                   # Detailed architecture (390+ lines)
├── CLAUDE.md                         # Project instructions for AI
└── README.md                         # Quick start guide
```

---

## 2. BACKEND ARCHITECTURE (Python 3.11+ FastAPI)

### 2.1 Core Application Entry Point

**File**: `backend/src/main.py` (199 lines)

- **FastAPI Setup**: Creates FastAPI app with CORS middleware
- **CORS Configuration**: Supports localhost:3000/9002, production domains (chat.chatbotpro.fr)
- **Route Registration**: Registers 6 API routers (auth, documents, conversations, chat, evaluations, embedding, admin)
- **Middleware**: Logging middleware for request/response tracking, CORS debugging
- **Service Initialization**: On startup, initializes:
  - Supabase client
  - MinIO service
  - Neo4j service
  - RAG service
- **Static Files**: Mounts `/uploads` directory for document serving
- **Health Check**: `/health` endpoint tests connectivity to all external services

### 2.2 Core Modules (`backend/src/core/`)

#### Configuration Management (`config.py` - 92 lines)
- **BaseSettings Pattern**: Uses pydantic-settings for environment variable management
- **File Size Parsing**: Custom parser for KB/MB/GB format strings
- **Validators**: 
  - Supabase URL validation (auto-prefix https://)
  - Boolean parsing for environment variables
  - Extension list parsing from comma-separated strings
- **Key Settings**:
  - Database credentials (Supabase URL, API key)
  - MinIO configuration (endpoint, credentials, bucket, SSL)
  - File upload limits (default 50MB)
  - Allowed file extensions (pdf, docx, txt, md, pptx, xlsx, etc.)
  - AI service keys (OpenAI, Cognee)
  - Embedding configuration (model, dimensions - configurable)

#### Database Connection (`database.py`)
- Supabase client initialization via service role key
- Singleton pattern for client management
- Connection pooling for async operations

#### Service Manager (`service_manager.py`)
- Singleton pattern for service instances
- Lazy initialization
- Prevents multiple instances of heavyweight services

#### Logging (`logger.py`)
- Structured logging via `loguru`
- Timestamps and context tracking
- Different log levels (DEBUG, INFO, WARNING, ERROR, SUCCESS)

### 2.3 API Routes (`backend/src/api/`)

#### 1. Authentication (`auth.py` - 9,985 lines)
**Endpoints**:
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login with JWT token generation
- `POST /auth/logout` - User session logout
- `GET /auth/me` - Get current authenticated user

**Key Features**:
- JWT-based authentication
- Token validation middleware (`get_current_user_from_token`)
- User creation in Supabase
- Session management
- Email-based authentication

#### 2. Documents (`documents.py` - 40,404 bytes)
**Endpoints**:
- `POST /documents/upload` - File upload to MinIO + database registration
- `GET /documents/` - List user's documents
- `GET /documents/{id}` - Get document details
- `DELETE /documents/{id}` - Delete document
- `POST /documents/start_ingestion` - Trigger embedding pipeline

**Key Features**:
- File validation (extension, size)
- Local file backup + MinIO storage
- Document metadata tracking in Supabase
- Unique file ID generation (UUID)
- Folder path support
- Status tracking (pending → embedding → complete)

#### 3. Chat (`chat.py` - 5,372 bytes)
**Endpoints**:
- `POST /chat` - Main chat interface with streaming support

**Key Features**:
- Conversation creation and management
- Message persistence in Supabase
- Conversation history retrieval (last 10 messages)
- RAG service integration for response generation
- Response streaming
- Citation extraction and formatting

**Data Flow**:
1. Receives ChatRequest (message + optional conversation_id)
2. Creates new conversation if needed
3. Saves user message to Supabase
4. Retrieves conversation history (last 10 messages)
5. Calls RAG service with query + history
6. Saves AI response
7. Returns ChatResponse with citations

#### 4. Conversations (`conversations.py`)
**Endpoints**:
- `GET /conversations/` - List conversation history
- `GET /conversations/{id}` - Get conversation details with messages
- `DELETE /conversations/{id}` - Delete conversation

#### 5. Evaluations (`evaluations.py` - 11,985 bytes)
**Endpoints**:
- `POST /evaluations/` - Submit evaluation/feedback for AI response
- `GET /evaluations/` - List evaluations (user or admin)

**Key Features**:
- Feedback collection on AI responses
- Rating system (1-5 stars)
- Comment collection
- Admin dashboard support

#### 6. Admin (`admin.py` - 16,041 bytes)
**Endpoints**:
- `GET /admin/evaluations` - View all evaluations
- Dashboard and analytics endpoints

### 2.4 Services (`backend/src/services/`) - Core Business Logic

#### Neo4j Service (`neo4j_service.py` - 565 lines)
**Responsibility**: Graph database operations

**Key Methods**:
- `initialize()` - Establish async driver connection
- `execute_query(query, params)` - Execute Cypher queries with parameters
- `create_node(label, properties)` - Create graph nodes
- `create_relationship(from_id, rel_type, to_id)` - Create relationships
- `find_related_nodes(node_id, max_hops)` - Graph traversal (2-hop limit)
- `vector_search(query_vector, limit)` - Cosine similarity search on embeddings
- `full_text_search(query_text, limit)` - Lucene full-text search

**Graph Structure**:
```
Document → contains → Chunk
Chunk → has_embedding → Vector[1536]
Chunk → extracted_entity → Entity (Person, Org, Location, etc.)
Entity → relationship → Entity (inferred relations)
```

**Indexing**:
- Vector index on embeddings (cosine similarity)
- Full-text index on entity names and chunk text
- Constraint indexes on node IDs

#### MinIO Service (`minio_service.py` - 164 lines)
**Responsibility**: Object storage operations

**Key Methods**:
- `initialize()` - Connect to MinIO
- `upload_file(file_bytes, filename, file_id)` - Upload to MinIO bucket
- `download_file(file_id)` - Retrieve file from MinIO
- `delete_file(file_id)` - Delete file
- `list_files(prefix)` - List files with optional prefix

**Configuration**:
- S3-compatible API
- Bucket: training-docs (configurable)
- SSL/TLS support
- Multipart upload for large files

#### RAG Service (`notaria_rag_service.py` - 1,079 lines)
**Responsibility**: Core RAG logic with PROTOCOLE DAN v5 (ReAct Architecture)

**Architecture Phases**:

1. **REASON Phase** (Query Analysis)
   - Analyzes user question + conversation history (last 10 messages)
   - Resolves coreferences ("cette négociation" → "négociation immobilière")
   - Expands legal synonyms ("recours" → "réclamation, conciliation, médiateur")
   - Formulates optimized search query
   - Model: `gpt-4.1-nano-2025-04-14` (fast, deterministic)

2. **ACT Phase** (Hybrid Search)
   - Parallel vector search (cosine similarity on 1536-dim embeddings)
   - Full-text search (Lucene index)
   - Result fusion and deduplication
   - LLM-based reranking for relevance scoring
   - Returns top-K scored chunks

3. **OBSERVE Phase** (Synthesis)
   - Context-aware response generation using top chunks
   - Maintains conversational context
   - Automatic citation extraction
   - Model: `gpt-4.1-2025-04-14` (high-quality synthesis)

**Key Methods**:
- `query(question, conversation_history)` - Main RAG query method
- `query_with_metrics(question, strategy)` - Legacy multi-strategy approach
- `_chunk_text_for_retrieval()` - Token-based chunking (512 tokens, 50 overlap)
- `_split_text_into_large_chunks()` - Large chunk splitting for analysis
- `_extract_entities_with_llm()` - LLM entity extraction
- `_embed_chunks()` - Batch embedding generation
- `_rerank_chunks()` - LLM-based result reranking

**Configuration**:
```yaml
Chunking:
  Chunk Size: 512 tokens (configurable)
  Overlap: 50 tokens
  Semantic aware: Respects paragraph boundaries

Embedding:
  Model: text-embedding-3-small (configurable)
  Dimensions: 1536 (can be 3072 or reduced)
  Batch size: 100 chunks

LLM Clients:
  Extraction: gpt-4.1-mini-2025-04-14
  Planner: gpt-4.1-nano-2025-04-14
  Synthesis: gpt-4.1-2025-04-14
  Endpoints: OpenAI or OpenRouter (configurable)
```

#### Ontology Service (`ontology_service.py` - 75 lines)
**Responsibility**: Domain ontology management

**Features**:
- OWL ontology loading
- Entity type definitions for legal domain
- Relationship type specifications

### 2.5 Data Models (`backend/src/models/schemas.py`)

**Key Pydantic Schemas**:
- `UserResponse` - User profile (id, email, full_name, created_date, is_admin)
- `DocumentResponse` - Document metadata (id, filename, file_size, status, indexing_status)
- `ChatRequest` - Chat input (message, conversation_id, document_ids)
- `ChatResponse` - Chat output (message, citations, conversation_id, metadata)
- `Citation` - Source attribution (documentId, documentPath, text)
- `MessageCreate` - Message storage schema
- `ConversationCreate` - Conversation schema
- `DocumentStatus` Enum: pending, embedding, complete, failed
- `IndexingStatus` Enum: pending, indexing, indexed, failed

### 2.6 Scripts (`backend/scripts/`) - CLI Tools

#### Document Ingestion Pipeline (`ingestion_pipeline.py`)
**Function**: Process documents from MinIO → extraction → chunking → embedding → Neo4j

**Process Flow**:
1. **Fetch Document**: Download from MinIO
2. **Text Extraction**: 
   - PyMuPDF for text-based PDFs (fast)
   - Docling for OCR/complex formats (accurate)
3. **Text Cleaning**: Remove encoding artifacts
4. **Semantic Chunking**: 512 token chunks with paragraph boundaries
5. **Entity Extraction**: LLM analysis of chunks
6. **Vector Embedding**: Batch generation via OpenAI
7. **Graph Storage**: Store chunks, entities, embeddings in Neo4j
8. **Status Tracking**: Update Supabase with completion status

**Modes**:
- Single batch: `python scripts/ingestion_pipeline.py`
- Daemon mode: `python scripts/ingestion_pipeline.py --daemon` (continuous monitoring)

#### Graph Enrichment Agent (`src/agents/graph_enrichment_agent.py`)
**Function**: Autonomous graph enhancement and inference

**Capabilities**:
- Transitive relationship inference
- Anomaly detection in graph
- Relationship inference between entities
- Knowledge graph expansion
- Continuous enrichment loop

#### Additional Scripts:
- `verify_minio.py` - Test MinIO connectivity
- `benchmark_quality_report.py` - Generate quality metrics
- `enrichment_pipeline.py` - Run graph enrichment

### 2.7 Testing Infrastructure (`backend/tests/`)

**Test Files** (16 modules):
- `test_core_config.py` - Configuration parsing
- `test_core_database.py` - Database connectivity
- `test_minio_service.py` - MinIO operations
- `test_neo4j_service.py` - Graph database operations
- `test_notaria_rag_service*.py` - RAG system (3 variants)
- `test_api_*.py` - API endpoint tests
- `test_routes_embedding.py` - Embedding route
- `test_all_services_integrated.py` - Integration tests

**Framework**: pytest with asyncio support
- Coverage target: 70% (configured in pyproject.toml)
- Current status: 60/60 core tests passing (100% pass rate)
- Test markers: @pytest.mark.unit, @pytest.mark.integration, @pytest.mark.slow
- Fixtures: conftest.py with singleton reset utilities

**Recent Improvements**:
- Fixed all 137 mypy type annotation errors
- Achieved 100% pass rate for 20/20 tests
- Comprehensive coverage for config, database, MinIO services

---

## 3. FRONTEND ARCHITECTURE (Next.js 15 + React 18 + TypeScript)

### 3.1 Project Configuration

**Technology Stack**:
- Framework: Next.js 15.5.0
- Runtime: Node.js with TypeScript 5.7.3
- Bundler: Turbopack (dev mode on port 9002)
- CSS: Tailwind CSS 3.4.1
- Component Library: Radix UI (25+ primitives)
- Form Management: React Hook Form + Zod validation
- HTTP Client: Fetch API + custom wrapper
- State Management: React Context API
- UI Icons: Lucide React (0.475.0)

### 3.2 App Router Structure (`front/src/app/`)

#### Authentication Routes (`(auth)` group)
- `/login` - User login page
- `/signup` - User registration
- `/forgot-password` - Password recovery
- `/reset-password` - Password reset

**Layout**: Unauthenticated layout with clean styling

#### Application Routes (`(app)` group)
- `/chat/[[...conversationId]]` - Main chat interface (dynamic routing)
- `/documents` - Document management interface
- `/` (root) - Application home/redirect

**Layout**: Protected layout with sidebar, header, authenticated context

### 3.3 Core Components (`front/src/components/`)

#### Layout Components:
- `app-sidebar.tsx` - Sidebar navigation with conversation history
- `auth-guard.tsx` - Route protection wrapper

#### Feature Components:
- `document-management.tsx` - Upload, list, delete documents
- `evaluation-component.tsx` - Feedback/rating system
- `citation-tooltip.tsx` - Source attribution display

#### UI Components (50+ from `ui/`):
- Buttons, inputs, textareas
- Forms with validation (form.tsx)
- Dialogs, modals, sheets
- Cards, tables, tabs
- Progress indicators, sliders
- Toast notifications, tooltips
- Dropdowns, select, radio groups
- Sidebar layout components

### 3.4 Contexts (`front/src/contexts/`)

**AuthContext.tsx**:
- Manages user authentication state
- Token storage and validation
- User profile caching
- Logout functionality
- Auth token refresh

### 3.5 Custom Hooks (`front/src/hooks/`)

- `use-mobile.tsx` - Detect mobile viewport
- `useCurrentUser.ts` - Get authenticated user
- `use-toast.ts` - Toast notification system

### 3.6 API Integration (`front/src/lib/`)

**api.ts** - API client wrapper
- Base URL configuration from `NEXT_PUBLIC_API_URL`
- Authentication token injection
- Request/response handling
- Error handling and logging

**types.ts** - TypeScript interfaces
- Chat message types
- Document types
- User types
- API response types

**utils.ts** - Utility functions
- String formatting
- Date formatting
- Class name merging (clsx)

### 3.7 AI Integration (`front/src/ai/`)

**genkit.ts**:
- Google Genkit initialization
- Model: `googleai/gemini-2.0-flash`
- Plugin: Google AI plugin

**flows/**:
- `summarize-conversation-title.ts` - Generate conversation titles

**dev.ts** - Development server for Genkit

---

## 4. DATA FLOW ARCHITECTURE

### 4.1 Authentication Flow

```
User → Frontend Login
  ↓
POST /api/auth/login
  ↓
Backend validates credentials
  ↓
Supabase authenticates user
  ↓
JWT token generated
  ↓
Response: token + user data
  ↓
Frontend stores token (localStorage)
  ↓
Subsequent requests include Authorization header
```

### 4.2 Document Ingestion Flow

```
User Upload (Frontend)
  ↓
POST /api/documents/upload
  ↓
Backend validates file (extension, size)
  ↓
Upload to MinIO (S3-compatible storage)
  ↓
Save document metadata to Supabase
  ↓
Return document_id
  ↓
POST /api/documents/start_ingestion
  ↓
Trigger ingestion_pipeline.py script
  ↓
Pipeline Process:
  ├─ Fetch from MinIO
  ├─ Extract text (PyMuPDF or Docling)
  ├─ Semantic chunking (512 tokens)
  ├─ Entity extraction (LLM)
  ├─ Vector embedding (OpenAI)
  └─ Store in Neo4j (graph + vectors)
  ↓
Update status in Supabase (complete/failed)
```

### 4.3 Chat Interaction Flow (PROTOCOLE DAN v5)

```
User Message (Frontend)
  ↓
POST /api/chat { message, conversation_id }
  ↓
Backend chat.py:
  1. Create/verify conversation
  2. Save user message to Supabase
  3. Retrieve conversation history (last 10 messages)
  ↓
RAG Service (notaria_rag_service.py):
  
  REASON Phase:
  ├─ Analyze question + history
  ├─ Resolve coreferences
  ├─ Expand legal synonyms
  └─ Formulate optimized query (gpt-4.1-nano)
  
  ACT Phase (Parallel):
  ├─ Vector search (cosine similarity)
  ├─ Full-text search (Lucene)
  ├─ Merge & deduplicate results
  └─ Rerank by relevance (gpt-4.1-nano)
  
  OBSERVE Phase:
  ├─ Generate response (gpt-4.1-2025)
  ├─ Extract citations
  └─ Format output
  ↓
Response: ChatResponse { message, citations, metadata }
  ↓
Backend saves AI response to Supabase
  ↓
Frontend displays message with source tooltips
```

### 4.4 Neo4j Graph Model

```
Document (id, title, user_id, upload_date)
  ├─ contains → Chunk (id, text, offset, embedding[1536])
  │           ├─ extracted_entity → Entity
  │           │                   (name, type: Person/Org/Location/Contract/Article)
  │           └─ has_embedding → Vector
  │
  └─ Chunk → extracted_entity → Entity
                              ├─ works_for → Organization
                              ├─ located_at → Location
                              ├─ references → Legal Article
                              └─ related_to → Entity (inferred)
```

---

## 5. CONFIGURATION & ENVIRONMENT MANAGEMENT

### 5.1 Backend Environment Variables

**Database**:
```
SUPABASE_URL=https://[instance].supabase.co
SUPABASE_KEY=[service_role_key]
```

**Neo4j**:
```
NEO4J_URL=bolt://[host]:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=[password]
```

**MinIO**:
```
MINIO_ENDPOINT=[domain]:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=[password]
MINIO_SECURE=true
MINIO_BUCKET_NAME=training-docs
```

**AI Services**:
```
OPENAI_API_KEY=[key]
LLM_API_KEY=[key]
LLM_ENDPOINT=https://openrouter.ai/api/v1

EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

LLM_EXTRACTION_MODEL=gpt-4.1-mini-2025-04-14
LLM_PLANNER_MODEL=gpt-4.1-nano-2025-04-14
LLM_SYNTHESIS_MODEL=gpt-4.1-2025-04-14
```

**Processing**:
```
ANALYSIS_CHUNK_SIZE_TOKENS=60000
RETRIEVAL_CHUNK_SIZE_TOKENS=512
RETRIEVAL_OVERLAP_TOKENS=50
```

### 5.2 Frontend Environment Variables

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://[instance].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[anon_key]
```

### 5.3 Configuration Files

**Backend**:
- `pyproject.toml` - Modern Python packaging (PEP 621)
  - Dependencies groups: core, [dev], [test]
  - Pytest configuration (70% coverage requirement)
  - Ruff/black/mypy settings
  - Package scripts: chatdocai, chatdocai-ingest, chatdocai-enrich

- `.env.example` - Template with all variables
- `pytest.ini` - Simplified pytest config

**Frontend**:
- `next.config.ts` - Next.js config (standalone output for Docker)
- `tsconfig.json` - TypeScript strict mode
- `tailwind.config.ts` - Tailwind CSS customization
- `.eslintrc.json` - ESLint rules
- `jest.config.js` - Jest testing setup

---

## 6. DEPLOYMENT & DOCKER

### 6.1 Docker Compose Setup

**Development** (`docker-compose.dev.yml`):
- Frontend service (port 9002, Turbopack hot reload)
- Backend service (port 8000, auto-reload)
- Supabase stack (local database)
- Volume mounts for source code

**Production** (`docker-compose.yml`):
- Frontend service (port 3000)
- Backend service (port 8000)
- Supabase stack
- Optimized images (no hot reload)

### 6.2 Makefile Commands

**Setup & Control**:
```bash
make setup           # Initialize .env files
make dev-start       # Start development services
make dev-stop        # Stop services
make dev-restart     # Restart services
make rebuild-backend # Rebuild backend only
make rebuild-frontend # Rebuild frontend only
```

**Access**:
```bash
make backend         # Open backend shell
make frontend        # Open frontend shell
make database        # Open database shell
```

**Testing & Quality**:
```bash
make test            # Run all tests
make test-backend    # Backend tests with coverage
make lint            # Lint all code
make format          # Format code
make typecheck       # Type checking
make pre-commit      # Full CI locally
```

---

## 7. KEY PATTERNS & ARCHITECTURE DECISIONS

### 7.1 Backend Patterns

**Singleton Pattern** (Services):
- Services are initialized once and reused
- `get_minio_service()`, `get_neo4j_service()`, `get_rag_service()`
- Prevents multiple database connections

**Dependency Injection**:
- FastAPI `Depends()` for request-scoped resources
- Supabase client injected into route handlers
- Services injected for business logic

**Async/Await**:
- All I/O operations are async
- Database queries, API calls, file operations
- Event loop configuration in pytest.ini

**Layered Architecture**:
```
API Routes (endpoints) ↓
Services (business logic) ↓
Core (configuration, database) ↓
External Services (Neo4j, MinIO, Supabase, OpenAI)
```

### 7.2 Frontend Patterns

**Next.js App Router**:
- File-based routing
- Route groups: (auth) and (app)
- Dynamic segments: [[...conversationId]]
- Standalone output for Docker

**React Context**:
- AuthContext for user state
- Replaces Redux for simpler state management

**Component Composition**:
- UI components from Radix primitives
- Feature components from Shadcn/ui recipes
- Page components use feature components

**Type Safety**:
- Full TypeScript throughout
- Zod for runtime validation
- Types exported from types.ts

### 7.3 RAG System Patterns

**Multi-Strategy Retrieval**:
- VECTOR_ONLY: Semantic matching
- GRAPH_FIRST: Relationship exploration
- HYBRID: Combined approach (default)

**Query Planning**:
- AI-powered strategy selection
- LLM analyzes query complexity
- Regex fallback for edge cases

**Response Generation**:
- Context-aware synthesis
- Conversational memory (last 10 messages)
- Automatic citation extraction
- Source attribution with confidence

---

## 8. ACTIVE DEVELOPMENT & RECENT CHANGES

### 8.1 Current Branch: `rag-bugfix`

**Modified Files** (9 total):
```
M ARCHITECTURE.md                    # Documentation updates
M CLAUDE.md                          # Project guidelines
M README.md                          # Quick start guide
M backend/.env.example               # Environment template
M backend/src/api/chat.py           # Chat endpoint fixes
M backend/src/api/evaluations.py    # Evaluation improvements
M backend/src/core/config.py        # Configuration updates
M backend/src/services/neo4j_service.py   # Graph service fixes
M backend/src/services/notaria_rag_service.py # RAG optimizations
```

**Untracked Files**:
```
?? backend/coverage.json             # Test coverage report
```

### 8.2 Recent Commits (Last 30)

**Latest Commits**:
1. `96d489a` - security: Fix npm audit vulnerabilities in frontend
2. `bf41b17` - test: Fix all failing tests and achieve 100% pass rate (20/20)
3. `176ca34` - fix(rag): Fix Neo4j graph traversal and implement PROTOCOLE DAN v2 optimizations
4. `5bc5269` - Merge pull request #43
5. `0c846b1` - fix prerender issue

**Key Themes**:
- RAG system optimization and bug fixes
- Neo4j graph traversal improvements
- Test suite completion and 100% pass rate
- Security vulnerability patching
- Documentation synchronization

### 8.3 Known Issues & Improvements

**Completed**:
- Fixed all 137 mypy type annotation errors
- Achieved 100% test pass rate (20/20 core tests)
- Implemented PROTOCOLE DAN v5 (ReAct architecture)
- Fixed Neo4j async session handling

**Test Coverage**:
- Current: ~28-30% (target: 70%)
- Core services: 60/60 tests passing
- Passing: config, database, MinIO services
- Needs work: RAG service, API integration tests

---

## 9. TECHNOLOGY INVENTORY

### 9.1 Backend Dependencies

**Core Framework**:
- fastapi>=0.110.0
- uvicorn[standard]>=0.27.0
- pydantic[email]>=2.6.0, pydantic-settings>=2.2.0

**Database & Storage**:
- neo4j>=5.25.0 (Graph DB)
- supabase>=2.3.0 (PostgreSQL + Auth)
- minio>=7.2.0 (S3-compatible object storage)

**Document Processing**:
- docling>=2.0.0 (Main parser - IBM Research)
- docling-core>=2.0.0, docling-parse>=2.0.0
- PyMuPDF>=1.26.3 (Fast PDF extraction)
- python-docx>=1.1.0 (DOCX parsing)
- openpyxl>=3.1.0 (Excel parsing)
- extract-msg>=0.48.0 (Email parsing)

**AI & ML**:
- openai>=1.50.0 (Embeddings + LLM calls)
- tiktoken>=0.10.0 (Token counting)

**Utilities**:
- python-dotenv>=1.0.0 (Environment loading)
- loguru>=0.7.0 (Structured logging)
- aiofiles>=23.2.1 (Async file operations)
- httpx>=0.26.0 (Async HTTP client)

**Testing** (Optional):
- pytest==8.3.4, pytest-asyncio==0.24.0
- pytest-cov==6.0.0, pytest-mock==3.14.0
- coverage[toml]==7.6.10

**Development** (Optional):
- ruff>=0.1.0 (Linting/formatting)
- mypy>=1.5.0 (Type checking)
- black>=23.0.0 (Code formatting)

### 9.2 Frontend Dependencies

**Framework & Core**:
- next@15.5.0
- react@18.3.1, react-dom@18.3.1
- typescript@5.7.3

**UI & Components**:
- @radix-ui/* (25+ component libraries)
- tailwindcss@3.4.1
- lucide-react@0.475.0

**Forms & Validation**:
- react-hook-form@7.54.2
- @hookform/resolvers@4.1.3
- zod@3.24.2

**Data & API**:
- @supabase/supabase-js@2.55.0
- fetch API (built-in)

**AI Integration**:
- genkit@1.14.1
- @genkit-ai/next@1.14.1
- @genkit-ai/googleai@1.14.1

**Utilities**:
- date-fns@3.6.0
- recharts@2.15.1
- class-variance-authority@0.7.1
- clsx@2.1.1

### 9.3 Dev Tools

**Backend**:
- pytest ecosystem (testing)
- ruff (linting)
- mypy (type checking)
- coverage (code coverage)

**Frontend**:
- jest@29.7.0
- eslint@8.57.1
- typescript (type checking)
- vitest@2.1.8 (alternative test runner)

---

## 10. CODE ORGANIZATION PRINCIPLES

### 10.1 Backend Code Quality

**Type Annotation**: Strict mypy configuration
- `disallow_untyped_defs = true`
- `disallow_any_generics = true`
- All 137 errors fixed

**Code Style**: Ruff formatter
- Line length: 100 characters
- Quote style: double quotes
- Import sorting: isort profile

**Testing**: Comprehensive pytest suite
- Unit tests: Core functionality
- Integration tests: Service interactions
- Coverage requirement: 70% minimum

### 10.2 Frontend Code Quality

**TypeScript**: Strict mode enabled
- No implicit any
- Strict null checks
- noImplicitReturns

**ESLint**: Configured with Next.js plugin
- React best practices
- Hook rules
- Accessibility checks

**Styling**: Tailwind CSS
- Utility-first approach
- Component classes via clsx
- Radix UI + Shadcn customization

---

## 11. NOTABLE ARCHITECTURAL FEATURES

### 11.1 Hybrid Document Processing
- **PyMuPDF First**: Fast text extraction for clean PDFs
- **Docling Fallback**: OCR capabilities for scanned documents
- **15+ Format Support**: PDF, DOCX, TXT, MD, EML, HTML, RTF, PPT, XLS, PNG, JPG, WAV, MP3, ASCIIDOC
- **Concurrent Processing**: Up to 2 documents simultaneously

### 11.2 Intelligent Query Processing (PROTOCOLE DAN v5)
- **ReAct Architecture**: Reason → Act → Observe
- **Conversational Memory**: Maintains context across turns
- **Synonym Expansion**: Legal domain-specific synonyms
- **Coreference Resolution**: Understands pronouns and implicit references
- **Intelligent Reranking**: LLM-scored relevance

### 11.3 Knowledge Graph Enrichment
- **Automatic Inference**: Transitive relationships
- **Anomaly Detection**: Identify inconsistencies
- **Continuous Learning**: Graph enrichment agent
- **Relationship Inference**: Discover new connections

### 11.4 Flexible Embedding Configuration
- **Pluggable Models**: text-embedding-3-small/large (configurable via ENV)
- **Adjustable Dimensions**: 1536 (default) or 3072 (or reduced)
- **No Reindexing**: Can change dimensions without rebuilding
- **Batch Processing**: 100 chunks per batch for efficiency

---

## 12. SUMMARY TABLE

| Aspect | Details |
|--------|---------|
| **Repository** | chatbot-CNCAC (rag-bugfix branch) |
| **Backend** | FastAPI, Python 3.11+, 1883 lines core services |
| **Frontend** | Next.js 15, React 18, TypeScript 5.7 |
| **Graph DB** | Neo4j (remote) - knowledge graphs + vectors |
| **Object Storage** | MinIO (remote) - S3-compatible |
| **Database** | Supabase PostgreSQL (remote) |
| **RAG System** | PROTOCOLE DAN v5 (ReAct) - hybrid vector + graph search |
| **Document Formats** | 15+ (PDF, DOCX, TXT, MD, EML, HTML, RTF, PPT, XLS, PNG, JPG, WAV, MP3) |
| **Embeddings** | text-embedding-3-small/large, 1536-3072 dims (configurable) |
| **LLM Models** | gpt-4.1-mini (extraction), gpt-4.1-nano (planning), gpt-4.1 (synthesis) |
| **Testing** | 16 test modules, 60/60 core tests passing, 70% coverage target |
| **Deployment** | Docker Compose (dev & prod), Makefile commands |
| **Documentation** | ARCHITECTURE.md (390+ lines), CLAUDE.md, README.md |
| **State** | Active development, 9 modified files, 100% test pass rate |

---

## 13. FILE STRUCTURE REFERENCE

**Total Source Lines of Code (SLOC)**: ~3,000+ (backend services) + ~5,000+ (frontend)

**Key File Counts**:
- Backend Python files: 25+ modules
- Frontend TypeScript files: 60+ components/pages/hooks
- Test files: 16 comprehensive modules
- Configuration files: 15+ (pyproject.toml, next.config.ts, docker-compose, etc.)
- Documentation: 5 major markdown files

**Largest Components**:
- notaria_rag_service.py: 1,079 lines
- neo4j_service.py: 565 lines
- documents.py: 40KB (full document management)
- admin.py: 16KB (dashboard)
- evaluations.py: 12KB (feedback system)

