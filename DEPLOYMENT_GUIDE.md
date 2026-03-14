# Deployment Guide - Meta-Orchestrator Switchboard

**Version**: 1.0
**Last Updated**: 2026-02-05
**Status**: Production Ready 🚀

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Docker Commands](#docker-commands)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites

- **Docker**: 24.0+ ([Install](https://docs.docker.com/get-docker/))
- **Docker Compose**: 2.20+ ([Install](https://docs.docker.com/compose/install/))
- **Git**: 2.40+
- **Make**: (optional, for convenience commands)

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/meta-orchestrator-switchboard.git
cd meta-orchestrator-switchboard

# 2. Copy environment file
cp .env.example .env

# 3. Build and start services
make build
make up

# 4. Verify health
make health

# 5. Access application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

---

## 💻 Local Development

### Using Docker Compose

```bash
# Start all services (attached mode - see logs)
docker-compose up

# Start in detached mode (background)
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild after code changes
docker-compose build
docker-compose up -d
```

### Using Makefile (Recommended)

```bash
# Build images
make build

# Start services
make up

# View logs
make logs

# Run tests
make test

# Stop services
make down

# Clean everything (including volumes)
make clean

# See all available commands
make help
```

### Hot Reload Development

For faster development iterations:

**Backend Hot Reload**:
```bash
# Edit backend/docker-compose.override.yml
version: '3.8'
services:
  backend:
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
```

**Frontend Hot Reload**:
```bash
# Run frontend locally (outside Docker)
cd frontend
npm install
npm run dev
# Access at http://localhost:5173
```

---

## 🏭 Production Deployment

### Option 1: Docker Compose (Single Server)

```bash
# 1. Configure production environment
cp .env.example .env.production
nano .env.production  # Set production values

# 2. Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# 3. Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Check health
curl http://your-domain.com/health
curl http://your-domain.com:8000/health
```

### Option 2: Kubernetes

**Prerequisites**:
- Kubernetes cluster (1.27+)
- kubectl configured
- Helm 3.12+

**Deploy**:
```bash
# 1. Create namespace
kubectl create namespace switchboard

# 2. Create secrets
kubectl create secret generic switchboard-secrets \
  --from-literal=database-password=$DB_PASSWORD \
  --from-literal=secret-key=$SECRET_KEY \
  --from-literal=openai-key=$OPENAI_API_KEY \
  -n switchboard

# 3. Deploy with Helm (if available)
helm install switchboard ./helm/switchboard \
  --namespace switchboard \
  --values helm/values.production.yaml

# Or apply manifests directly
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml
```

### Option 3: Cloud Platforms

#### AWS ECS

```bash
# 1. Create ECR repositories
aws ecr create-repository --repository-name switchboard-backend
aws ecr create-repository --repository-name switchboard-frontend

# 2. Build and push images
docker build -t switchboard-backend:latest ./backend
docker tag switchboard-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/switchboard-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/switchboard-backend:latest

# 3. Create ECS task definition and service
aws ecs create-cluster --cluster-name switchboard-cluster
aws ecs create-service --cli-input-json file://ecs-service.json
```

#### Google Cloud Run

```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/$PROJECT_ID/switchboard-backend ./backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/switchboard-frontend ./frontend

# 2. Deploy to Cloud Run
gcloud run deploy switchboard-backend \
  --image gcr.io/$PROJECT_ID/switchboard-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

gcloud run deploy switchboard-frontend \
  --image gcr.io/$PROJECT_ID/switchboard-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Container Instances

```bash
# 1. Create resource group
az group create --name switchboard-rg --location eastus

# 2. Create container registry
az acr create --resource-group switchboard-rg --name switchboardacr --sku Basic

# 3. Build and push
az acr build --registry switchboardacr --image switchboard-backend:latest ./backend
az acr build --registry switchboardacr --image switchboard-frontend:latest ./frontend

# 4. Deploy containers
az container create \
  --resource-group switchboard-rg \
  --name switchboard-backend \
  --image switchboardacr.azurecr.io/switchboard-backend:latest \
  --cpu 2 --memory 4 \
  --ports 8000
```

---

## ⚙️ Environment Configuration

### Essential Variables

```env
# Database
POSTGRES_DB=switchboard
POSTGRES_USER=switchboard
POSTGRES_PASSWORD=<strong-password>

# Backend
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-strong-key>
CORS_ORIGINS=https://your-domain.com

# External Services
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Generate Strong Secrets

```bash
# Generate SECRET_KEY (Python)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate POSTGRES_PASSWORD (OpenSSL)
openssl rand -base64 32
```

### Environment-Specific Files

- `.env.development` - Local development
- `.env.staging` - Staging environment
- `.env.production` - Production environment

Load specific environment:
```bash
docker-compose --env-file .env.production up
```

---

## 🐳 Docker Commands

### Build Commands

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend

# Build with no cache (clean build)
docker-compose build --no-cache

# Build with specific Dockerfile
docker build -f Dockerfile.prod -t switchboard-backend:prod ./backend
```

### Run Commands

```bash
# Start services
docker-compose up
docker-compose up -d  # Detached mode

# Scale services
docker-compose up -d --scale backend=3

# Run one-time command
docker-compose run --rm backend python -c "print('Hello')"

# Execute in running container
docker-compose exec backend bash
docker-compose exec db psql -U switchboard
```

### Inspect & Debug

```bash
# View logs
docker-compose logs -f --tail=100

# Check container stats
docker stats

# Inspect container
docker inspect switchboard-backend

# View container processes
docker-compose top

# Check health
docker ps --filter "health=unhealthy"
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Full cleanup
docker system prune -a --volumes
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

The project includes automated CI/CD via GitHub Actions (`.github/workflows/ci-cd.yml`):

**Triggers**:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`

**Pipeline Stages**:

1. **Backend Tests** (5-10 min)
   - Linting (black, isort, flake8, mypy)
   - Security scan (bandit, safety)
   - Unit tests (pytest)
   - Integration tests
   - Coverage report

2. **Frontend Tests** (3-5 min)
   - Linting (eslint, prettier)
   - Type checking (TypeScript)
   - Unit tests (Jest)
   - Build verification

3. **Docker Build** (5-10 min)
   - Multi-stage image builds
   - Push to Docker Hub
   - Cache optimization

4. **Security Scan** (2-3 min)
   - Trivy vulnerability scanner
   - SARIF upload to GitHub Security

5. **Deploy** (2-5 min, only on `main`)
   - Deployment to production
   - Health checks
   - Notifications

**Required Secrets**:
```bash
# GitHub Repository → Settings → Secrets → Actions
DOCKERHUB_USERNAME=your-username
DOCKERHUB_TOKEN=dckr_pat_...
KUBE_CONFIG=<base64-encoded-kubeconfig>
```

### Manual Deployment

```bash
# Build and tag
docker build -t your-org/switchboard-backend:v1.0.0 ./backend
docker build -t your-org/switchboard-frontend:v1.0.0 ./frontend

# Push to registry
docker push your-org/switchboard-backend:v1.0.0
docker push your-org/switchboard-frontend:v1.0.0

# Deploy
kubectl set image deployment/backend backend=your-org/switchboard-backend:v1.0.0
kubectl rollout status deployment/backend
```

---

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Check service health
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "switchboard-api", "version": "1.0.0"}

curl http://localhost/health
# Expected: OK

# Using Makefile
make health
```

### Database Backups

```bash
# Backup database
docker-compose exec db pg_dump -U switchboard switchboard > backup_$(date +%Y%m%d).sql

# Restore database
cat backup_20260205.sql | docker-compose exec -T db psql -U switchboard switchboard
```

### Log Management

```bash
# View recent logs
docker-compose logs --tail=1000

# Export logs
docker-compose logs > logs_$(date +%Y%m%d_%H%M%S).txt

# Rotate logs
docker-compose restart  # Restarts and rotates logs
```

### Performance Monitoring

```bash
# Container resource usage
docker stats

# Database connections
docker-compose exec db psql -U switchboard -c "SELECT count(*) FROM pg_stat_activity;"

# API metrics
curl http://localhost:8000/api/analytics/system
```

### Updates & Upgrades

```bash
# 1. Pull latest changes
git pull origin main

# 2. Rebuild images
make build

# 3. Stop old containers
make down

# 4. Start new containers
make up

# 5. Verify
make health
```

---

## 🔧 Troubleshooting

### Common Issues

#### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Check for port conflicts
lsof -i :8000
lsof -i :80

# Check if image built correctly
docker images | grep switchboard
```

#### Database Connection Error

```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec db psql -U switchboard -d switchboard -c "SELECT 1;"

# Verify DATABASE_URL
docker-compose exec backend env | grep DATABASE_URL
```

#### Permission Errors

```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Reset volumes
docker-compose down -v
docker-compose up -d
```

#### Out of Memory

```bash
# Check Docker resources
docker system df

# Clean up
docker system prune -a

# Increase Docker memory (Docker Desktop)
# Settings → Resources → Memory → Increase to 4GB+
```

#### Slow Performance

```bash
# Check resource usage
docker stats

# Optimize images
# - Use multi-stage builds ✓
# - Minimize layers ✓
# - Use .dockerignore ✓

# Enable BuildKit
export DOCKER_BUILDKIT=1
docker-compose build
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/api/docs
- **Architecture Diagram**: `docs/architecture.md`
- **Database Schema**: `docs/database-schema.md`
- **Kubernetes Guide**: `docs/kubernetes-deployment.md`
- **Security Guide**: `docs/security-best-practices.md`

---

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/switchboard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/switchboard/discussions)
- **Email**: support@your-domain.com

---

**Last Updated**: 2026-02-05
**Version**: 1.0.0
**Status**: ✅ Production Ready
