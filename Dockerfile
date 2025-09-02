# Multi-stage build for optimized image size
FROM node:20-alpine AS frontend-builder

# Install build dependencies
RUN apk add --no-cache python3 make g++

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig*.json ./
COPY vite.config.ts ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY index.html ./
COPY src ./src
COPY public ./public

# Build frontend
RUN npm run build

# Python backend stage
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Final production image
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1001 cleaner && \
    mkdir -p /app /var/log/supervisor /var/log/nginx /var/cache/nginx && \
    chown -R cleaner:cleaner /app /var/log /var/cache/nginx

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy frontend build
COPY --from=frontend-builder /app/dist ./dist

# Copy application code
COPY api_server.py ./
COPY config.py ./
COPY cleaner_engine.py ./
COPY src ./src
COPY cleaner ./cleaner

# Copy configuration files
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/cache /app/models && \
    chown -R cleaner:cleaner /app

# Switch to non-root user
USER cleaner

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    NODE_ENV=production

# Expose ports
EXPOSE 80 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start services with supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]