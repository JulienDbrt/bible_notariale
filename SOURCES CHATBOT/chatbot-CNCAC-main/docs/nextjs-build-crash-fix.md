# 🚨 Fix Crash Next.js Build - Solution Immédiate

## 🔍 Problème Identifié

Le crash survient à l'étape `next build` - "Creating an optimized production build". Causes probables :

1. **Manque de mémoire** lors du build
2. **Variables d'environnement manquantes** pour les dépendances (Genkit AI, Firebase)
3. **Problème de configuration** Next.js 15.3.3
4. **Erreurs dans le code source** qui bloquent le build

## 🚀 Solution Immédiate : Dockerfile de Contournement

Remplacez **complètement** le contenu de [`front/Dockerfile`](front/Dockerfile:1) par :

```dockerfile
# Solution de contournement pour Next.js 15.3.3
FROM node:18-alpine

WORKDIR /app

# Installer les dépendances système nécessaires
RUN apk add --no-cache \
    libc6-compat \
    curl \
    bash

# Augmenter les limites de mémoire Node.js
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Copier les fichiers package
COPY package.json package-lock.json* ./

# Installer les dépendances
RUN npm ci --production=false

# Copier le code source
COPY . .

# Créer le dossier public si manquant
RUN mkdir -p public

# Variables d'environnement pour le build
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV SKIP_ENV_VALIDATION=1

# Désactiver les optimisations qui peuvent causer des crashes
ENV NEXT_PRIVATE_SKIP_SIZE_ANALYSIS=1

# Build avec gestion d'erreur
RUN echo "Starting Next.js build..." && \
    npm run build || \
    (echo "Build failed, trying fallback..." && \
     NODE_ENV=development npm run build)

# Créer l'utilisateur pour la sécurité
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs && \
    chown -R nextjs:nodejs /app

USER nextjs

# Port d'exposition
EXPOSE 3000

# Variables d'environnement runtime
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Démarrer l'application
CMD ["npm", "start"]
```

## 🔧 Alternative Ultra-Simple (Si Build Continue à Crash)

Si le build continue à crasher, utilisez cette version **sans build** :

```dockerfile
# Version développement pour contourner le problème de build
FROM node:18-alpine

WORKDIR /app

# Dépendances système
RUN apk add --no-cache libc6-compat curl

# Augmenter mémoire
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Copier package files
COPY package.json package-lock.json* ./

# Installer dépendances
RUN npm ci

# Copier code source
COPY . .

# Créer dossiers nécessaires
RUN mkdir -p public .next

# Créer utilisateur
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs && \
    chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

# Variables
ENV NODE_ENV=development
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Lancer en mode dev (plus stable)
CMD ["npm", "run", "dev", "--", "--port", "3000", "--hostname", "0.0.0.0"]
```

## ⚙️ Configuration Dokploy Critique

### Variables d'Environnement à Ajouter

```bash
# Mémoire et performance
NODE_OPTIONS=--max-old-space-size=4096
NEXT_PRIVATE_SKIP_SIZE_ANALYSIS=1
SKIP_ENV_VALIDATION=1

# Next.js
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1

# Supabase (si nécessaires au build)
NEXT_PUBLIC_SUPABASE_URL=https://[votre-projet].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[votre-clé]

# API Backend
NEXT_PUBLIC_API_URL=https://[votre-backend-url]
```

### Augmenter les Ressources Dokploy

Dans Dokploy, configurez :
- **CPU** : 2 vCPU minimum
- **Mémoire** : 2GB minimum pour le build
- **Timeout** : 600 secondes

## 🧪 Test de Debug Local

Pour identifier exactement où ça crash :

```bash
cd front

# Test avec plus de logs
DEBUG=* npm run build 2>&1 | tee build-debug.log

# Test avec mémoire augmentée
NODE_OPTIONS="--max-old-space-size=4096" npm run build

# Test sans optimisations
NEXT_PRIVATE_SKIP_SIZE_ANALYSIS=1 npm run build
```

## 🔍 Causes Spécifiques Probables

### 1. Problème Genkit AI
Les dépendances [`package.json`](front/package.json:44-45) `firebase` et `genkit` peuvent causer des problèmes de build.

**Solution temporaire** : Commentez dans [`package.json`](front/package.json:1) :
```json
{
  "dependencies": {
    // "@genkit-ai/googleai": "^1.14.1",
    // "@genkit-ai/next": "^1.14.1",
    // "firebase": "^11.9.1",
    // "genkit": "^1.14.1",
```

### 2. Problème de Code Source
Vérifiez s'il y a des erreurs TypeScript :
```bash
cd front
npm run typecheck
```

### 3. Problème de Configuration
Vérifiez [`next.config.ts`](front/next.config.ts:1) - la ligne `output: 'standalone'` peut poser problème avec Next.js 15.

## 🆘 Solution d'Urgence : Déploiement Sans Build

Si rien ne marche, déployez temporairement sans build optimisé :

```dockerfile
FROM node:18-alpine
WORKDIR /app
RUN apk add --no-cache libc6-compat
COPY package.json ./
RUN npm install
COPY . .
EXPOSE 3000
ENV NODE_ENV=development
CMD ["npm", "run", "dev", "--", "--port", "3000"]
```

## ✅ Actions Prioritaires

1. **Remplacer le Dockerfile** par la première version
2. **Ajouter les variables d'environnement** dans Dokploy
3. **Augmenter les ressources** (CPU/Mémoire)
4. **Tester le déploiement**
5. Si crash continue : utiliser la version sans build

Cette approche devrait résoudre le crash lors de `next build` en contournant les optimisations problématiques de Next.js 15.3.3.
