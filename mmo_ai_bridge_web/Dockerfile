# MMO AI Bridge - Docker Container
# Version: 1.0
# Production-ready Docker image

FROM python:3.10-slim

LABEL maintainer="AI Research Assistant"
LABEL version="1.0"
LABEL description="MMO AI Bridge - Visualize AI/ML systems as RPG characters"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directory for database
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=server.py
ENV PYTHONUNBUFFERED=1
ENV DATABASE_PATH=/app/data/mmo_ai_bridge.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')"

# Run with gunicorn for production
CMD ["python", "server.py"]
