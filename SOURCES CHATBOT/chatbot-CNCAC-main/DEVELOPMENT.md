# ChatDocAI - Development Guide

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd chatbot-CNCAC

# Quick setup with Makefile
make setup          # Creates all .env files
make dev-start      # Starts all services
```

## Development Workflow

### Backend Development

#### Local Development (without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (modern approach with pyproject.toml)
pip install -e ".[dev]"  # Installs package in editable mode with dev dependencies

# Or if you still have requirements.txt (legacy)
pip install -r requirements.txt
pip install -r requirements-test.txt  # Test dependencies

# Run development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Dependency Management

The project now uses `pyproject.toml` for modern dependency management:
- **Production dependencies**: Listed in `[project] dependencies`
- **Development dependencies**: Available via `pip install -e ".[dev]"`
- **Test dependencies only**: Available via `pip install -e ".[test]"`

#### Testing

```bash
cd backend

# Install test dependencies first
pip install -e ".[test]"

# Run all tests
pytest

# Run with coverage (configured in pyproject.toml)
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_neo4j_service.py

# Run tests by marker
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only

# Run tests matching pattern
pytest -k "test_vector_search"

# Verbose output
pytest -vv
```

### Frontend Development

#### Local Development

```bash
cd front

# Install dependencies
npm install

# Run development server
npm run dev

# Other commands
npm run build        # Production build
npm run lint         # Run ESLint
npm run typecheck    # TypeScript check
npm run lint:fix     # Auto-fix linting issues
```

#### Component Development

The project uses Radix UI primitives. To add new UI components:

```bash
# Example: Add a new dialog component
npx shadcn@latest add dialog
```

### Docker Development

#### Essential Commands

```bash
# Start all services
make dev-start

# View logs
make dev-logs

# Stop services
make dev-stop

# Rebuild specific service
make rebuild-backend
make rebuild-frontend

# Clean everything
make dev-clean
```

#### Accessing Containers

```bash
# Backend shell
docker-compose -f docker-compose.dev.yml exec backend bash

# Frontend shell
docker-compose -f docker-compose.dev.yml exec frontend sh

# Run backend tests in container
docker-compose -f docker-compose.dev.yml exec backend pytest
```

## Code Organization

### Backend Structure

```
backend/src/
├── api/            # API endpoints
│   ├── auth.py     # Authentication endpoints
│   ├── chat.py     # Chat functionality
│   ├── documents.py # Document management
│   └── conversations.py
├── core/           # Core configuration
│   ├── config.py   # Settings management
│   └── database.py # Database connections
├── models/         # Data models
│   └── schemas.py  # Pydantic schemas
├── services/       # Business logic
│   ├── neo4j_service.py      # Graph database
│   ├── minio_service.py      # Object storage
│   └── notaria_rag_service.py # RAG engine
└── agents/         # Autonomous agents
    └── graph_enrichment_agent.py
```

### Frontend Structure

```
front/src/
├── app/            # Next.js App Router
│   ├── (app)/      # Protected routes
│   └── (auth)/     # Auth routes
├── components/     # React components
│   ├── ui/         # Radix UI primitives
│   └── ...         # Feature components
├── lib/            # Utilities
│   ├── api.ts      # API client
│   ├── supabase.ts # Supabase client
│   └── types.ts    # TypeScript types
├── contexts/       # React contexts
└── ai/             # Genkit configuration
```

## Environment Configuration

### Backend Environment Variables

```bash
# Database
SUPABASE_URL=https://your-instance.supabase.co
SUPABASE_KEY=your_service_role_key

# Neo4j
NEO4J_URL=bolt://your-neo4j:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# MinIO
MINIO_ENDPOINT=your-minio.domain.com
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
MINIO_BUCKET=documents

# OpenAI
OPENAI_API_KEY=your_openai_key

# Optional: Model Configuration
LLM_EXTRACTION_MODEL=gpt-4o-mini
LLM_PLANNER_MODEL=gpt-4o-mini
LLM_SYNTHESIS_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small

# App Configuration
UPLOAD_DIR=/tmp/uploads
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_EXTENSIONS=pdf,docx,txt,md,eml,html,rtf
```

### Frontend Environment Variables

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-instance.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key

# Optional: Feature Flags
NEXT_PUBLIC_ENABLE_ADMIN=true
NEXT_PUBLIC_ENABLE_FEEDBACK=true
```

## Common Development Tasks

### Adding a New API Endpoint

1. Create route in `backend/src/api/your_module.py`:
```python
from fastapi import APIRouter, Depends
from src.models.schemas import YourSchema
from src.api.auth import get_current_user

router = APIRouter(prefix="/api/your-route", tags=["your-tag"])

@router.post("/")
async def your_endpoint(
    data: YourSchema,
    current_user = Depends(get_current_user)
):
    # Implementation
    return {"result": "success"}
```

2. Register in `backend/src/main.py`:
```python
from src.api import your_module

app.include_router(your_module.router)
```

3. Add frontend API client in `front/src/lib/api.ts`:
```typescript
export const yourApi = {
  async yourMethod(data: YourType) {
    return apiRequest<YourResponse>('/api/your-route', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
```

### Working with the Database

#### Supabase Migrations

```sql
-- Create in Supabase SQL Editor
CREATE TABLE your_table (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    data JSONB
);

-- Enable RLS
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;

-- Add policy
CREATE POLICY "Users can access own data" ON your_table
    FOR ALL USING (auth.uid() = user_id);
```

#### Neo4j Queries

```python
# In backend/src/services/neo4j_service.py
async def your_query():
    query = """
    MATCH (n:YourNode)
    WHERE n.property = $value
    RETURN n
    """
    result = await self.driver.execute_query(
        query,
        value="your_value"
    )
    return result
```

### Document Processing

#### Manual Document Ingestion

```bash
cd backend

# Single document
python scripts/ingestion_pipeline.py

# Continuous monitoring
python scripts/ingestion_pipeline.py --daemon

# With specific settings
BATCH_SIZE=10 python scripts/ingestion_pipeline.py
```

#### Graph Enrichment

```bash
# Run enrichment agent
python -m src.agents.graph_enrichment_agent

# Check graph statistics
python -c "from src.services.neo4j_service import Neo4jService; 
          service = Neo4jService(); 
          print(service.get_statistics())"
```

## Debugging

### Backend Debugging

```python
# Add in your code for debugging
import pdb; pdb.set_trace()

# Or use logging
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Variable value: {variable}")
```

### Frontend Debugging

```typescript
// Add debug logging
console.log('[DEBUG]', 'Component rendered', { props });

// Use React DevTools
// Install browser extension for component inspection

// Debug API calls
window.localStorage.setItem('debug', 'true');
// This enables detailed API logging
```

### Docker Debugging

```bash
# View all container logs
docker-compose -f docker-compose.dev.yml logs

# Follow specific service logs
docker-compose -f docker-compose.dev.yml logs -f backend

# Check container status
docker-compose -f docker-compose.dev.yml ps

# Inspect network
docker network inspect chatbot-cncac_app-network
```

## Performance Optimization

### Backend Optimization

1. **Database Queries**
   - Use parameterized queries
   - Implement query result caching
   - Create appropriate indexes

2. **Document Processing**
   - Batch embeddings generation
   - Implement concurrent processing
   - Cache processed documents

3. **API Response**
   - Use pagination for large datasets
   - Implement response compression
   - Add appropriate caching headers

### Frontend Optimization

1. **Bundle Size**
   - Use dynamic imports for large components
   - Implement code splitting
   - Tree-shake unused dependencies

2. **Rendering**
   - Use React.memo for expensive components
   - Implement virtual scrolling for lists
   - Optimize re-renders with useCallback/useMemo

3. **Data Fetching**
   - Implement SWR or React Query
   - Use optimistic updates
   - Prefetch data when possible

## Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check if ports are in use
lsof -i :8000

# Check environment variables
python -c "from src.core.config import settings; print(settings)"

# Verify database connections
python scripts/check_connections.py
```

#### Frontend Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
npm run dev

# Check for type errors
npm run typecheck

# Fix linting issues
npm run lint:fix
```

#### Docker Issues
```bash
# Reset everything
docker-compose down -v
docker system prune -af
docker-compose up --build

# Check disk space
docker system df
```

## Best Practices

### Code Style

#### Python (Backend)
- Follow PEP 8
- Use type hints
- Write docstrings for functions
- Keep functions small and focused

#### TypeScript (Frontend)
- Use strict mode
- Define interfaces for all data structures
- Avoid any type
- Use functional components with hooks

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "feat: add your feature"

# Push and create PR
git push origin feature/your-feature
```

### Commit Messages
Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Tests
- `chore:` Maintenance

## Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [Supabase Docs](https://supabase.com/docs)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [Neo4j Browser](https://neo4j.com/developer/neo4j-browser/) - Graph exploration
- [React DevTools](https://react.dev/learn/react-developer-tools) - Component debugging