# Multi-stage build for Next.js
FROM node:20-alpine as base

# Install dependencies for building
RUN apk add --no-cache libc6-compat curl

# Set working directory
WORKDIR /app

# Development stage
FROM base as development

# Optimiser npm pour moins de mémoire
ENV NPM_CONFIG_CACHE=/tmp/.npm
ENV NODE_OPTIONS="--max-old-space-size=1024"

# Copy source code first to get updated package.json
COPY . .

# Install dependencies (this will use the updated package.json)
RUN npm install --no-audit --no-fund

# Create public folder
RUN mkdir -p public

# Create user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Change ownership of everything to nextjs user
RUN chown -R nextjs:nodejs /app /tmp/.npm

# Environment variables
ENV NODE_ENV=development
ENV PORT=9002
ENV HOSTNAME=0.0.0.0

USER nextjs

EXPOSE 9002

# Development command with hot reload
CMD ["npm", "run", "dev", "--", "--port", "9002", "--hostname", "0.0.0.0"]

# Production builder stage
FROM base as builder

ENV NODE_OPTIONS="--max-old-space-size=2048"

COPY package.json package-lock.json* ./
RUN npm ci --no-audit --no-fund && npm cache clean --force

COPY . .

# Declare build arguments with default values
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_SUPABASE_URL=http://localhost:8000
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY=dummy_key_for_build

# Set environment variables from build arguments
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY

RUN npm run build

# Production stage
FROM node:20-alpine as production

RUN apk add --no-cache curl

WORKDIR /app

# Create user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs

EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

CMD ["node", "server.js"]
