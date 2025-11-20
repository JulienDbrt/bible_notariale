# ChatDocAI - Deployment Guide

## Production Deployment Overview

This guide covers deploying ChatDocAI to production environments with proper security, scalability, and monitoring.

## Prerequisites

### Required Services
- **Neo4j**: Graph database (Aura or self-hosted)
- **MinIO**: Object storage (or S3-compatible alternative)
- **Supabase**: PostgreSQL database and authentication
- **OpenAI API**: For embeddings and LLM operations

### Infrastructure Requirements
- **Compute**: 4 vCPUs, 8GB RAM minimum
- **Storage**: 50GB+ for documents
- **Network**: HTTPS with valid SSL certificates
- **Domain**: For production URLs

## Deployment Options

### Option 1: Docker Compose (Single Server)

Best for: Small to medium deployments, proof of concept

```bash
# Clone repository
git clone <repository-url>
cd chatbot-CNCAC

# Configure production environment
cp .env.production.example .env
# Edit .env with production values

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Setup SSL with Nginx
sudo apt install nginx certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Option 2: Kubernetes Deployment

Best for: Large scale, high availability requirements

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatdocai-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatdocai-backend
  template:
    metadata:
      labels:
        app: chatdocai-backend
    spec:
      containers:
      - name: backend
        image: your-registry/chatdocai-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: SUPABASE_URL
          valueFrom:
            secretKeyRef:
              name: chatdocai-secrets
              key: supabase-url
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
```

Apply with:
```bash
kubectl apply -f k8s/
```

### Option 3: Cloud Platform Deployment

#### AWS Deployment

```bash
# Using AWS Copilot
copilot app init chatdocai
copilot env init --name production
copilot svc deploy --name backend --env production
copilot svc deploy --name frontend --env production
```

#### Google Cloud Platform

```bash
# Using Cloud Run
gcloud run deploy chatdocai-backend \
  --image gcr.io/PROJECT-ID/chatdocai-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars="SUPABASE_URL=xxx"
```

#### Azure Container Instances

```bash
az container create \
  --resource-group chatdocai-rg \
  --name chatdocai \
  --image your-registry.azurecr.io/chatdocai:latest \
  --dns-name-label chatdocai \
  --ports 80 443
```

## Production Configuration

### Environment Variables

Create `.env.production`:

```bash
# Application
NODE_ENV=production
API_URL=https://api.your-domain.com

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-production-key

# Neo4j (Production Cluster)
NEO4J_URL=neo4j+s://your-neo4j.aura.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=strong-password-here

# MinIO/S3
MINIO_ENDPOINT=s3.amazonaws.com
MINIO_ACCESS_KEY=AKIA...
MINIO_SECRET_KEY=...
MINIO_BUCKET=chatdocai-production
MINIO_USE_SSL=true

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...

# Security
JWT_SECRET=generate-strong-secret-here
CORS_ORIGINS=https://your-domain.com

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
ENABLE_METRICS=true
```

### Security Hardening

#### 1. SSL/TLS Configuration

```nginx
# /etc/nginx/sites-available/chatdocai
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 2. Firewall Rules

```bash
# UFW configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

#### 3. Secrets Management

Use a secrets manager for production:

```python
# backend/src/core/config.py
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name):
    """Retrieve secret from AWS Secrets Manager"""
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name='us-east-1'
    )
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except ClientError as e:
        raise e

# Use in settings
class Settings(BaseSettings):
    openai_api_key: str = Field(default_factory=lambda: get_secret('chatdocai/openai'))
```

## Database Setup

### Neo4j Production Setup

#### Using Neo4j Aura (Recommended)

1. Create account at [Neo4j Aura](https://neo4j.com/cloud/aura/)
2. Create new database instance
3. Save connection details
4. Create indexes:

```cypher
-- Performance indexes
CREATE INDEX chunk_embedding IF NOT EXISTS FOR (c:Chunk) ON (c.embedding);
CREATE INDEX doc_id IF NOT EXISTS FOR (d:Document) ON (d.id);
CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name);
CREATE FULLTEXT INDEX entity_search IF NOT EXISTS FOR (n:Entity) ON EACH [n.name, n.description];
```

#### Self-Hosted Neo4j

```bash
# Install Neo4j
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update
sudo apt install neo4j

# Configure for production
sudo vi /etc/neo4j/neo4j.conf
# Set:
# dbms.memory.heap.initial_size=2g
# dbms.memory.heap.max_size=4g
# dbms.connector.bolt.listen_address=0.0.0.0:7687

sudo systemctl restart neo4j
```

### Supabase Configuration

1. **Enable Row Level Security (RLS)**:

```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can read own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can read own documents" ON documents
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can read own conversations" ON conversations
    FOR SELECT USING (auth.uid() = user_id);
```

2. **Setup Database Backups**:
   - Enable Point-in-Time Recovery in Supabase dashboard
   - Configure daily backups
   - Test restore procedures

### MinIO/S3 Configuration

```bash
# For MinIO production
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=admin \
  -e MINIO_ROOT_PASSWORD=strong-password \
  -v /data/minio:/data \
  minio/minio server /data --console-address ":9001"

# Configure bucket
mc alias set myminio http://localhost:9000 admin strong-password
mc mb myminio/documents
mc policy set download myminio/documents
```

## Monitoring & Logging

### Application Monitoring

#### Prometheus + Grafana Setup

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
      
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
```

#### Application Metrics

```python
# backend/src/core/metrics.py
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
request_count = Counter('app_requests_total', 'Total requests')
request_duration = Histogram('app_request_duration_seconds', 'Request duration')
document_processed = Counter('documents_processed_total', 'Documents processed')
rag_queries = Counter('rag_queries_total', 'RAG queries', ['strategy'])

# Expose metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Logging Configuration

#### Centralized Logging with ELK Stack

```yaml
# docker-compose.logging.yml
version: '3.8'
services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - es_data:/usr/share/elasticsearch/data
      
  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
      
  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
```

#### Application Logging

```python
# backend/src/core/logging.py
import logging
from pythonjsonlogger import jsonlogger

# Configure JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Use in application
logger.info("Document processed", extra={
    "document_id": doc_id,
    "processing_time": time_taken,
    "chunks_created": chunk_count
})
```

## Backup & Recovery

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

# Set variables
BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup Neo4j
neo4j-admin dump --to=$BACKUP_DIR/neo4j-backup.dump

# Backup MinIO
mc mirror myminio/documents $BACKUP_DIR/minio-backup/

# Backup Supabase (via pg_dump)
PGPASSWORD=$DB_PASSWORD pg_dump \
  -h $DB_HOST \
  -U $DB_USER \
  -d $DB_NAME \
  > $BACKUP_DIR/supabase-backup.sql

# Upload to S3
aws s3 sync $BACKUP_DIR s3://backup-bucket/chatdocai/

# Clean old backups (keep 30 days)
find /backups -type d -mtime +30 -exec rm -rf {} \;
```

Add to crontab:
```bash
0 2 * * * /opt/chatdocai/backup.sh
```

## Performance Tuning

### Backend Optimization

```python
# backend/src/main.py

# Enable response compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configure connection pooling
from databases import Database
database = Database(
    DATABASE_URL,
    min_size=10,
    max_size=20,
    max_queries=50,
    max_inactive_connection_lifetime=300,
)

# Add caching
from fastapi_cache import FastAPICache
from fastapi_cache.backend.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="chatdocai-cache:")
```

### Frontend Optimization

```javascript
// next.config.js
module.exports = {
  images: {
    domains: ['your-cdn.com'],
    loader: 'cloudinary',
  },
  compress: true,
  poweredByHeader: false,
  generateEtags: true,
  
  // Enable SWC minification
  swcMinify: true,
  
  // Standalone output for Docker
  output: 'standalone',
}
```

## Health Checks

### Backend Health Check

```python
# backend/src/api/health.py
from fastapi import APIRouter, status
from src.services.neo4j_service import Neo4jService
from src.core.database import supabase

router = APIRouter()

@router.get("/health")
async def health_check():
    checks = {
        "api": "healthy",
        "neo4j": "unknown",
        "supabase": "unknown",
        "minio": "unknown"
    }
    
    try:
        # Check Neo4j
        neo4j = Neo4jService()
        await neo4j.verify_connection()
        checks["neo4j"] = "healthy"
    except:
        checks["neo4j"] = "unhealthy"
    
    try:
        # Check Supabase
        supabase.table("users").select("id").limit(1).execute()
        checks["supabase"] = "healthy"
    except:
        checks["supabase"] = "unhealthy"
    
    # Return appropriate status code
    if all(v == "healthy" for v in checks.values()):
        return checks
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=checks
        )
```

### Docker Health Checks

```dockerfile
# backend/Dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# frontend/Dockerfile  
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1
```

## Scaling Strategies

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  backend:
    image: chatdocai-backend
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        
  nginx:
    image: nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - backend
```

### Load Balancing

```nginx
# nginx.conf
upstream backend {
    least_conn;
    server backend1:8000 weight=5;
    server backend2:8000 weight=5;
    server backend3:8000 weight=5;
}

server {
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Disaster Recovery

### Recovery Procedures

1. **Database Recovery**:
```bash
# Restore Neo4j
neo4j-admin load --from=backup.dump --database=neo4j

# Restore Supabase
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < backup.sql

# Restore MinIO
mc mirror backup/ myminio/documents
```

2. **Rollback Procedure**:
```bash
# Keep previous versions
docker tag chatdocai:latest chatdocai:previous
docker build -t chatdocai:latest .

# Rollback if needed
docker tag chatdocai:previous chatdocai:latest
docker-compose up -d
```

## Maintenance

### Regular Maintenance Tasks

```bash
# Weekly tasks
- Review error logs
- Check disk usage
- Update dependencies
- Run security scans

# Monthly tasks
- Review performance metrics
- Optimize database queries
- Clean up old documents
- Test backup restoration

# Quarterly tasks
- Security audit
- Dependency updates
- Performance review
- Disaster recovery drill
```

## Troubleshooting Production Issues

### Common Issues and Solutions

| Issue | Symptoms | Solution |
|-------|----------|----------|
| High Memory Usage | OOM kills, slow response | Increase heap size, optimize queries |
| Slow Queries | Timeout errors | Add indexes, implement caching |
| Connection Errors | 502/503 errors | Check service health, increase connection pool |
| Storage Full | Upload failures | Clean old files, increase storage |
| Rate Limiting | 429 errors | Adjust limits, implement queue |

### Debug Commands

```bash
# Check resource usage
docker stats

# View service logs
docker-compose logs -f backend

# Database connections
netstat -an | grep 5432

# Check disk usage
df -h

# Memory usage
free -m

# Process list
ps aux | grep python
```