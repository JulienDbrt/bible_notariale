# Spécification Technique - Application de Chat IA Self-Hosted

## Architecture Générale

**Stack principal :**
- Frontend : React 18+ avec TypeScript
- Backend : FastAPI avec Python 3.11
- Base de données : Supabase self-hosted (PostgreSQL)
- Conteneurisation : Docker + Docker Compose
- Réseau : Bridge Docker interne

## Infrastructure Docker

### Services
```yaml
services:
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    environment:
      - REACT_APP_API_URL=http://backend:8000
      - REACT_APP_SUPABASE_URL=http://supabase:54321
    networks: [app-network]

  backend:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - SUPABASE_URL=http://supabase:54321
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - UPLOAD_DIR=/app/uploads
    volumes: ["documents_storage:/app/uploads"]
    networks: [app-network]

  supabase:
    # Supabase self-hosted stack
    ports: ["54321:54321"]
    networks: [app-network]

volumes:
  documents_storage:
  supabase_data:

networks:
  app-network:
    driver: bridge
```

## Frontend React

### Pages et Fonctionnalités

**Page Chat (`/chat`) :**
- Interface de chat avec historique en temps réel
- Zone de saisie avec support markdown
- Affichage formaté des réponses IA
- Sidebar historique des conversations
- Bouton nouvelle conversation

**Page Documents (`/documents`) :**
- Liste des documents (nom, taille, date, statut)
- Zone drag & drop pour upload
- Actions par document : télécharger, supprimer, statut
- Bouton "Knowledge Graph" (URL depuis API)
- Bouton "Lancer embedding"
- Indicateurs de progression

### Stack Technique Frontend
- React 18+ avec TypeScript
- Tailwind CSS pour le styling
- React Router v6 pour navigation
- Axios pour appels API
- React Query pour state management et cache
- React Hook Form pour formulaires
- React Context pour état global
- Supabase JS client

### Structure des données Frontend
```typescript
interface Conversation {
  id: string;
  title: string;
  created_date: string;
}

interface Message {
  id: string;
  conversation_id: string;
  content: string;
  is_user: boolean;
  timestamp: string;
}

interface Document {
  id: string;
  filename: string;
  file_path: string;
  upload_date: string;
  file_size: number;
  status: 'uploaded' | 'processing' | 'embedded' | 'error';
}
```

## Backend FastAPI

### Endpoints API

**Endpoints principaux (à implémenter) :**
- `POST /search` : Recherche dans documents
- `POST /embed` : Processus d'embedding

**Endpoints CRUD :**
- `POST /upload` : Upload vers `/app/uploads`
- `GET /documents` : Liste des documents
- `DELETE /documents/{id}` : Suppression document
- `GET /documents/{id}/download` : Téléchargement
- `GET /conversations` : Liste conversations
- `POST /conversations` : Créer conversation
- `GET /conversations/{id}/messages` : Messages conversation
- `POST /conversations/{id}/messages` : Nouveau message
- `GET /knowledge-graph` : URL du knowledge graph

### Stack Technique Backend
- FastAPI avec Python 3.11
- Pydantic pour validation
- Cognee 
- Supabase-py pour DB
- Uvicorn comme serveur ASGI
- SQLAlchemy pour ORM (optionnel)
- Multipart pour upload fichiers

### Format des Réponses API
```python
# Réponse standard
{
  "success": bool,
  "data": Any,
  "message": str,
  "errors": List[str]
}

# Upload response
{
  "success": true,
  "data": {
    "document_id": "uuid",
    "filename": "example.pdf",
    "file_size": 1024000
  }
}
```

## Base de Données Supabase

### Configuration
- Supabase self-hosted via Docker
- Migration automatique au démarrage
- Seed data initial
- Policies configurées (lecture/écriture libre)

### Schéma des Tables
```sql
-- Conversations
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  created_date TIMESTAMP DEFAULT NOW()
);

-- Messages
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  is_user BOOLEAN NOT NULL,
  timestamp TIMESTAMP DEFAULT NOW()
);

-- Documents
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  filename VARCHAR(255) NOT NULL,
  file_path VARCHAR(500) NOT NULL,
  upload_date TIMESTAMP DEFAULT NOW(),
  file_size BIGINT NOT NULL,
  status VARCHAR(20) DEFAULT 'uploaded'
);

-- Jobs d'embedding
CREATE TABLE embeddings_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  status VARCHAR(20) DEFAULT 'pending',
  progress INTEGER DEFAULT 0,
  created_date TIMESTAMP DEFAULT NOW()
);
```

### Seed Data Initial
```sql
INSERT INTO conversations (title) VALUES ('Conversation de test');
INSERT INTO messages (conversation_id, content, is_user)
SELECT id, 'Bonjour !', true FROM conversations LIMIT 1;
```

## Gestion des Fichiers

### Structure des Volumes
```
/app/uploads/
├── documents/
│   ├── {uuid}/{original_filename}
└── temp/
    └── {upload_session}/
```

### Mapping Fichiers
- Stockage : Volume Docker `documents_storage:/app/uploads`
- Nommage : `{uuid}/{filename}` pour éviter conflits
- DB field `file_path` : chemin relatif depuis `/app/uploads`
- Cleanup automatique des fichiers orphelins

## Variables d'Environnement

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SUPABASE_URL=http://localhost:54321
REACT_APP_SUPABASE_ANON_KEY=your_anon_key
```

### Backend (.env)
```
SUPABASE_URL=http://supabase:54321
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=50MB
ALLOWED_EXTENSIONS=pdf,docx,txt,md
```

## Fonctionnalités Spéciales

### État Global Frontend
- React Query pour cache API et synchronisation
- React Context pour état utilisateur
- Local storage pour préférences UI

### Gestion Temps Réel
- Polling pour updates conversations/documents
- WebSockets optionnel pour chat en temps réel

### Configuration Build
- Multi-stage Docker builds pour optimisation
- Health checks sur tous les services
- Logs centralisés avec rotation

Cette spécification est-elle complète et claire pour l'implémentation ?
