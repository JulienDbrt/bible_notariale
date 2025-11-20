# Guide de Déploiement Dokploy - Chatbot Notaires

## 🎯 Vue d'ensemble

Ce guide vous permet de déployer votre chatbot sur Dokploy avec une architecture simplifiée :
- **Frontend** : Next.js (port 3000)
- **Backend** : FastAPI (port 8000)
- **Base de données** : Supabase existant (déjà configuré)

## 📋 Pré-requis

- ✅ Instance Dokploy opérationnelle
- ✅ Supabase configuré avec URL et clés API
- ✅ Accès Git au repository du projet
- ✅ Domaine configuré (optionnel mais recommandé)

### Architecture Recommandée
```
Internet → Reverse Proxy → Frontend (3000) → Backend (8000) → Supabase
```

### Ordre de Déploiement
1. **Backend** (déployer en premier - indépendant)
2. **Frontend** (déployer après - dépend du backend)

## 🔧 Configuration Backend (Service 1)

### 1. Créer l'Application Backend

Dans Dokploy :

```bash
# Navigation Dokploy
Applications → Create Application → Docker
```

**Configuration générale :**
- **Nom** : `chatbot-backend`
- **Repository** : `[votre-repo-git]`
- **Branch** : `main`
- **Build Path** : `./backend`
- **Dockerfile Path** : `./backend/Dockerfile`
- **Target Stage** : `production`

### 2. Variables d'Environnement Backend

```bash
# Configuration Supabase (OBLIGATOIRE)
SUPABASE_URL=https://[votre-projet].supabase.co
SUPABASE_ANON_KEY=[votre-clé-anon]
SUPABASE_SERVICE_ROLE_KEY=[votre-clé-service]

# Configuration Upload
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=50000000
ALLOWED_EXTENSIONS=pdf,docx,txt,md,pptx,xlsx

# Configuration Application
PYTHONPATH=/app/src
ENVIRONMENT=production

# CORS (à adapter selon votre domaine)
ALLOWED_ORIGINS=https://[votre-domaine-frontend]
```

### 3. Configuration Réseau Backend

```bash
# Port Configuration
Container Port: 8000
Host Port: 8000 (ou auto-assign)

# Health Check (déjà dans Dockerfile)
Health Check URL: /health
```

### 4. Volume Backend

```bash
# Volume pour les uploads
Volume Name: chatbot-uploads
Mount Path: /app/uploads
Type: Named Volume
```

### 5. Commandes de Déploiement Backend

```bash
# Build et deploy
docker build -t chatbot-backend -f backend/Dockerfile --target production ./backend
```

## 🎨 Configuration Frontend (Service 2)

### 1. Créer l'Application Frontend

Dans Dokploy :

```bash
# Navigation Dokploy
Applications → Create Application → Docker
```

**Configuration générale :**
- **Nom** : `chatbot-frontend`
- **Repository** : `[votre-repo-git]`
- **Branch** : `main`
- **Build Path** : `./front`
- **Dockerfile Path** : `./front/Dockerfile`
- **Target Stage** : `runner` (production)

### 2. Variables d'Environnement Frontend

```bash
# Configuration Next.js
NODE_ENV=production
PORT=3000
HOSTNAME=0.0.0.0

# Configuration Supabase (côté client)
NEXT_PUBLIC_SUPABASE_URL=https://[votre-projet].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[votre-clé-anon]

# Configuration API Backend
NEXT_PUBLIC_API_URL=https://[votre-backend-url]:8000
# ou si même domaine : NEXT_PUBLIC_API_URL=/api

# Configuration Application
NEXT_PUBLIC_APP_NAME="Chatbot Notaires"
NEXT_PUBLIC_APP_VERSION="1.0.0"
```

### 3. Configuration Réseau Frontend

```bash
# Port Configuration
Container Port: 3000
Host Port: 3000 (ou 80/443 si domaine principal)

# Dependencies
Depends On: chatbot-backend
```

### 4. Commandes de Déploiement Frontend

```bash
# Build et deploy
docker build -t chatbot-frontend -f front/Dockerfile --target runner ./front
```

## 🌐 Configuration DNS et Domaines

### Option 1 : Sous-domaines Séparés
```bash
# Configuration DNS
api.votredomaine.com → Backend (8000)
app.votredomaine.com → Frontend (3000)
```

### Option 2 : Même Domaine avec Reverse Proxy
```bash
# Configuration Nginx/Traefik
votredomaine.com/api/* → Backend (8000)
votredomaine.com/* → Frontend (3000)
```

## 📝 Checklist de Déploiement

### Avant le Déploiement

- [ ] Repository Git accessible depuis Dokploy
- [ ] Variables Supabase collectées et testées
- [ ] Domaines DNS configurés
- [ ] Certificats SSL configurés (si nécessaire)

### Déploiement Backend

- [ ] Application backend créée dans Dokploy
- [ ] Variables d'environnement configurées
- [ ] Volume uploads configuré
- [ ] Build et déploiement réussis
- [ ] Health check `/health` répond 200
- [ ] Test API avec `curl https://[backend-url]/health`

### Déploiement Frontend

- [ ] Application frontend créée dans Dokploy
- [ ] Variables d'environnement configurées
- [ ] Référence backend configurée
- [ ] Build et déploiement réussis
- [ ] Interface accessible
- [ ] Test communication frontend → backend

### Tests Post-Déploiement

- [ ] Page d'accueil charge correctement
- [ ] Connexion Supabase fonctionnelle
- [ ] Upload de documents fonctionne
- [ ] Chat interface répond
- [ ] Logs sans erreur dans Dokploy

## 🔨 Scripts Utiles

### Script de Test Backend
```bash
#!/bin/bash
BACKEND_URL="https://[votre-backend-url]"

echo "Testing backend health..."
curl -f "$BACKEND_URL/health" || exit 1

echo "Testing backend API..."
curl -f "$BACKEND_URL/api/health" || exit 1

echo "Backend tests passed!"
```

### Script de Test Frontend
```bash
#!/bin/bash
FRONTEND_URL="https://[votre-frontend-url]"

echo "Testing frontend..."
curl -I "$FRONTEND_URL" | grep "200 OK" || exit 1

echo "Frontend test passed!"
```

### Script de Déploiement Complet
```bash
#!/bin/bash
set -e

echo "🚀 Deploying Chatbot to Dokploy..."

# 1. Deploy Backend
echo "📦 Deploying Backend..."
# Déclenchement via webhook Dokploy ou CLI
curl -X POST "[dokploy-webhook-backend]"

# Attendre le déploiement
sleep 60

# 2. Test Backend
echo "🧪 Testing Backend..."
curl -f "https://[backend-url]/health" || exit 1

# 3. Deploy Frontend
echo "🎨 Deploying Frontend..."
curl -X POST "[dokploy-webhook-frontend]"

# Attendre le déploiement
sleep 60

# 4. Test Frontend
echo "🧪 Testing Frontend..."
curl -I "https://[frontend-url]" | grep "200 OK" || exit 1

echo "✅ Deployment completed successfully!"
```

## 🐛 Troubleshooting

### Problèmes Backend Courants

**1. Erreur de connexion Supabase**
```bash
# Vérifier les variables
docker exec [container-id] env | grep SUPABASE

# Tester la connexion
docker exec [container-id] curl -H "apikey: $SUPABASE_ANON_KEY" "$SUPABASE_URL/rest/v1/"
```

**2. Volume uploads non accessible**
```bash
# Vérifier le volume
docker volume inspect chatbot-uploads

# Vérifier les permissions
docker exec [container-id] ls -la /app/uploads
```

**3. Health check échoue**
```bash
# Vérifier les logs
docker logs [container-id]

# Tester manuellement
docker exec [container-id] curl localhost:8000/health
```

### Problèmes Frontend Courants

**1. Impossible de joindre le backend**
```bash
# Vérifier la variable API_URL
docker exec [container-id] env | grep API_URL

# Tester depuis le container
docker exec [container-id] curl [backend-url]/health
```

**2. Build Next.js échoue**
```bash
# Vérifier les logs de build
docker logs [container-id]

# Problème courant : standalone output
# S'assurer que next.config.ts contient :
output: 'standalone'
```

**3. Variables d'environnement non définies**
```bash
# Les variables NEXT_PUBLIC_* doivent être définies au build time
# Redéployer si modifiées
```

### Commandes de Debug Utiles

```bash
# Logs en temps réel
docker logs -f [container-id]

# Accès shell au container
docker exec -it [container-id] /bin/sh

# Vérifier le réseau
docker network ls
docker network inspect [network-name]

# Vérifier les volumes
docker volume ls
docker volume inspect [volume-name]

# Stats des containers
docker stats

# Informations détaillées
docker inspect [container-id]
```

## 📞 Support

En cas de problème :

1. **Vérifier les logs** Dokploy et containers
2. **Tester les endpoints** individuellement
3. **Vérifier la configuration** Supabase
4. **Consulter la documentation** Dokploy

## ✅ Résumé

Votre déploiement Dokploy est configuré avec :

- ✅ **Backend FastAPI** sur port 8000 avec health check
- ✅ **Frontend Next.js** sur port 3000 avec build optimisé
- ✅ **Volume persistant** pour les uploads
- ✅ **Connexion Supabase** existante
- ✅ **Sécurité** avec utilisateurs non-root
- ✅ **Monitoring** avec health checks

**Recommandation finale** : Déployez d'abord le backend, testez-le, puis déployez le frontend. Cette approche garantit une mise en service progressive et un debugging facilité.
