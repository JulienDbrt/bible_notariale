# Multi-stage build for optimized Python FastAPI container
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Development stage
FROM base as development

WORKDIR /app

# Create virtual environment
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional development dependencies
RUN pip install --no-cache-dir \
    watchfiles \
    pytest \
    pytest-asyncio \
    httpx

# Create non-root user for security with proper home directory
RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser -m appuser
RUN mkdir -p /app/uploads /app/src /home/appuser/.cache && chown -R appuser:appuser /app /home/appuser

# Copy source code and scripts
COPY src/ /app/src/
COPY scripts/ /app/scripts/
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Development command with auto-reload
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Builder stage for production
FROM base as builder

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    HOME=/home/appuser

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security with proper home directory
RUN groupadd -r appuser && useradd -r -g appuser -d /home/appuser -m appuser

# Create app directory and uploads directory
WORKDIR /app
RUN mkdir -p /app/uploads /app/src /home/appuser/.cache && chown -R appuser:appuser /app /home/appuser

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code and scripts
COPY src/ /app/src/
COPY scripts/ /app/scripts/

# Change ownership of application files
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]