# 🚨 Correction Dockerfile Frontend - Problèmes Critiques

## 🔍 Problèmes Identifiés

### 1. **Incompatibilité Next.js 15.3.3**
- Votre [`package.json`](front/package.json:47) utilise Next.js 15.3.3
- Le [`Dockerfile`](front/Dockerfile:1) est conçu pour Next.js 14
- `output: 'standalone'` a changé en Next.js 15

### 2. **Problème de Configuration Port**
- [`package.json`](front/package.json:6) : `dev: "next dev --turbopack -p 9002"`
- [`Dockerfile`](front/Dockerfile:73) : `ENV PORT 3000`
- **Conflit** : développement sur 9002, production sur 3000

### 3. **Variables d'Environnement Legacy**
- Warnings Docker : `ENV key=value` vs `ENV key value`
- Lignes 51, 73, 74 du Dockerfile

### 4. **Dependencies Complexes**
- Genkit AI, Firebase, etc. peuvent causer des problèmes de build
- [`package.json`](front/package.json:44-45) : `firebase`, `genkit`

## 🔧 Solution : Nouveau Dockerfile

### Dockerfile Corrigé

```dockerfile
# Multi-stage build for Next.js 15
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./
RUN npm ci --only=production && npm cache clean --force

# Development stage
FROM base AS development
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci
COPY . .

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NODE_ENV=development

CMD ["npm", "run", "dev"]

# Build stage
FROM base AS builder
WORKDIR /app

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set build environment variables
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Build the application
RUN npm run build

# Production stage
FROM base AS runner
WORKDIR /app

# Production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Create user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Create necessary directories
RUN mkdir -p .next /app/public
RUN chown -R nextjs:nodejs .next /app/public

# Copy public files (handle missing public folder gracefully)
COPY --from=builder --chown=nextjs:nodejs /app/public* ./public/ || echo "No public folder"

# Copy Next.js build output
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || curl -f http://localhost:3000/ || exit 1

# Start the application
CMD ["node", "server.js"]
```

## 🚀 Actions Immédiates

### 1. **Créer le nouveau Dockerfile**

Remplacez complètement le contenu de [`front/Dockerfile`](front/Dockerfile:1) par le code ci-dessus.

### 2. **Créer un Health Check Endpoint**

Ajoutez [`front/src/app/api/health/route.ts`](front/src/app/api/health/route.ts:1) :

```typescript
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0'
  });
}
```

### 3. **Variables d'Environnement Dokploy**

Configurez ces variables dans Dokploy :

```bash
# Build-time (nécessaires au build)
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1

# Runtime (nécessaires à l'exécution)
NEXT_PUBLIC_SUPABASE_URL=https://[votre-projet].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=[votre-clé]
NEXT_PUBLIC_API_URL=https://[votre-backend]

# Configuration Application
PORT=3000
HOSTNAME=0.0.0.0
```

## 🔄 Alternative Simple (si problème persist)

Si le Dockerfile multi-stage continue à poser problème, utilisez cette version simplifiée :

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN apk add --no-cache libc6-compat curl

# Copy package files
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source code
COPY . .

# Create public directory if missing
RUN mkdir -p public

# Build the application
RUN npm run build

# Create user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
RUN chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

# Environment variables
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Start the application
CMD ["npm", "start"]
```

## 🔍 Debug et Tests

### Test Local

```bash
# Test du build local
cd front
docker build -t test-frontend-simple .

# Test de l'exécution
docker run -p 3000:3000 -e NODE_ENV=production test-frontend-simple

# Vérifier que ça fonctionne
curl http://localhost:3000
```

### Logs de Debug

```bash
# Voir les logs détaillés du build
docker build --no-cache --progress=plain -t test-frontend .

# Voir les logs du container en marche
docker logs -f [container-id]
```

## ✅ Checklist de Correction

- [ ] Nouveau Dockerfile créé
- [ ] Health check endpoint ajouté
- [ ] Variables d'environnement configurées dans Dokploy
- [ ] Test local réussi
- [ ] Build Dokploy sans erreur
- [ ] Application démarre sans crash
- [ ] Health check répond correctement

## 🆘 Si Ça Ne Marche Toujours Pas

Utilisez cette approche de debugging étape par étape :

1. **Test build uniquement** :
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["echo", "Build successful"]
```

2. **Test simple sans build** :
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

Le problème principal est l'incompatibilité entre votre configuration Next.js 15 et le Dockerfile optimisé pour Next.js 14. La solution simplifiée devrait résoudre les crashes immédiatement.
