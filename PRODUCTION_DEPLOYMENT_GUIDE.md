# 🚀 Production Deployment Guide - Meta-Orchestrator Switchboard

**Version**: 1.0
**Last Updated**: 2026-02-05
**Target Environment**: Production (Kubernetes or Docker Compose)

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [Option A: Docker Compose Deployment](#option-a-docker-compose-deployment)
4. [Option B: Kubernetes Deployment](#option-b-kubernetes-deployment)
5. [Database Setup](#database-setup)
6. [Environment Configuration](#environment-configuration)
7. [Security Hardening](#security-hardening)
8. [SSL/TLS Setup](#ssltls-setup)
9. [Monitoring & Logging](#monitoring--logging)
10. [Backup & Recovery](#backup--recovery)
11. [Performance Tuning](#performance-tuning)
12. [Health Checks](#health-checks)
13. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum Requirements**:
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Disk**: 50 GB SSD
- **Network**: 100 Mbps

**Recommended for Production**:
- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Disk**: 200+ GB NVMe SSD
- **Network**: 1 Gbps

### Software Requirements

- **Docker**: 20.10+ (for Docker Compose deployment)
- **Docker Compose**: 2.0+ (for Docker Compose deployment)
- **Kubernetes**: 1.24+ (for K8s deployment)
- **kubectl**: 1.24+ (for K8s deployment)
- **PostgreSQL**: 14+ (if not using Docker)
- **Redis**: 7+ (if not using Docker)
- **nginx**: 1.20+ (for reverse proxy)

### Domain & SSL

- **Domain name** (e.g., `orchestrator.example.com`)
- **SSL certificate** (Let's Encrypt or commercial)
- **DNS** configured to point to your server

---

## Deployment Options

### Option A: Docker Compose (Recommended for Small-Medium Scale)

**Pros**:
- ✅ Simple setup
- ✅ All services in one configuration
- ✅ Easy to maintain
- ✅ Good for 1-3 servers

**Cons**:
- ❌ Limited scalability
- ❌ Manual load balancing
- ❌ No automatic failover

**Use Cases**:
- Small to medium deployments (< 10K requests/day)
- Development/staging environments
- Single server deployments

### Option B: Kubernetes (Recommended for Large Scale)

**Pros**:
- ✅ Auto-scaling
- ✅ High availability
- ✅ Self-healing
- ✅ Rolling updates
- ✅ Service mesh support

**Cons**:
- ❌ Complex setup
- ❌ Requires K8s knowledge
- ❌ Higher resource overhead

**Use Cases**:
- Large deployments (> 10K requests/day)
- Multi-region deployments
- Mission-critical applications

---

## Option A: Docker Compose Deployment

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/data7.git
cd data7
git checkout main  # or specific version tag
```

### Step 2: Configure Environment

Create production environment file:

```bash
cp .env.example .env.production
```

Edit `.env.production`:

```bash
# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-strong-secret-key>  # Use: openssl rand -hex 32

# Database
DATABASE_URL=postgresql://switchboard:STRONG_PASSWORD@postgres:5432/switchboard_prod
POSTGRES_USER=switchboard
POSTGRES_PASSWORD=<generate-strong-password>
POSTGRES_DB=switchboard_prod

# Redis
REDIS_URL=redis://:REDIS_PASSWORD@redis:6379/0
REDIS_PASSWORD=<generate-strong-password>

# JWT Authentication
JWT_SECRET_KEY=<generate-strong-jwt-key>  # Use: openssl rand -hex 64
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (adjust for your domain)
CORS_ORIGINS=["https://orchestrator.example.com"]

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=<generate-strong-password>

# Email (for alerts)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=alerts@example.com
SMTP_PASSWORD=<smtp-password>
SMTP_FROM=alerts@example.com
```

### Step 3: Generate Secrets

```bash
# Generate secret key
openssl rand -hex 32

# Generate JWT key
openssl rand -hex 64

# Generate strong passwords
openssl rand -base64 32
```

### Step 4: Build and Deploy

```bash
# Build images
docker-compose -f docker-compose.phase9.yml build

# Start services
docker-compose -f docker-compose.phase9.yml up -d

# Check status
docker-compose -f docker-compose.phase9.yml ps
```

### Step 5: Run Migrations

```bash
# Run database migrations
docker-compose -f docker-compose.phase9.yml exec backend alembic upgrade head
```

### Step 6: Create Admin User

```bash
# Access backend container
docker-compose -f docker-compose.phase9.yml exec backend python

# Create admin user
from app.auth.jwt import create_user
from app.infrastructure import get_db

async def create_admin():
    async for db in get_db():
        user = await create_user(
            db,
            username="admin",
            email="admin@example.com",
            password="STRONG_ADMIN_PASSWORD",
            roles=["superadmin"]
        )
        print(f"Admin user created: {user.id}")

import asyncio
asyncio.run(create_admin())
```

### Step 7: Setup nginx Reverse Proxy

Create `/etc/nginx/sites-available/orchestrator`:

```nginx
upstream backend {
    server localhost:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name orchestrator.example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name orchestrator.example.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/orchestrator.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/orchestrator.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend (React SPA)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket timeouts
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }

    # Monitoring (restrict access)
    location /metrics {
        allow 10.0.0.0/8;  # Internal network only
        deny all;
        proxy_pass http://backend;
    }

    # Health Check
    location /health {
        proxy_pass http://backend;
        access_log off;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/orchestrator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 8: Setup SSL with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d orchestrator.example.com

# Auto-renewal (cron)
sudo crontab -e
# Add: 0 0 * * * certbot renew --quiet
```

### Step 9: Verify Deployment

```bash
# Check all services
docker-compose -f docker-compose.phase9.yml ps

# Check logs
docker-compose -f docker-compose.phase9.yml logs -f backend

# Test API
curl https://orchestrator.example.com/health

# Test WebSocket
wscat -c wss://orchestrator.example.com/ws/events
```

---

## Option B: Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (GKE, EKS, AKS, or self-hosted)
- `kubectl` configured
- Helm 3+ installed
- Persistent storage class available

### Step 1: Create Namespace

```bash
kubectl create namespace switchboard-prod
kubectl config set-context --current --namespace=switchboard-prod
```

### Step 2: Create Secrets

```bash
# Database password
kubectl create secret generic postgres-secret \
  --from-literal=password=$(openssl rand -base64 32)

# Redis password
kubectl create secret generic redis-secret \
  --from-literal=password=$(openssl rand -base64 32)

# JWT secret
kubectl create secret generic jwt-secret \
  --from-literal=secret-key=$(openssl rand -hex 64)

# Application secret
kubectl create secret generic app-secret \
  --from-literal=secret-key=$(openssl rand -hex 32)
```

### Step 3: Create ConfigMap

Create `configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: switchboard-config
  namespace: switchboard-prod
data:
  ENVIRONMENT: "production"
  DEBUG: "false"
  DATABASE_HOST: "postgres-service"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "switchboard_prod"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  JWT_ALGORITHM: "HS256"
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "15"
  JWT_REFRESH_TOKEN_EXPIRE_DAYS: "7"
  CORS_ORIGINS: '["https://orchestrator.example.com"]'
  PROMETHEUS_ENABLED: "true"
```

Apply:

```bash
kubectl apply -f configmap.yaml
```

### Step 4: Deploy PostgreSQL

Create `postgres-deployment.yaml`:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: switchboard-prod
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-ssd  # Adjust to your storage class
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: switchboard-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:14
        env:
        - name: POSTGRES_DB
          value: "switchboard_prod"
        - name: POSTGRES_USER
          value: "switchboard"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: switchboard-prod
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

Apply:

```bash
kubectl apply -f postgres-deployment.yaml
```

### Step 5: Deploy Redis

Create `redis-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: switchboard-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
        - redis-server
        - --requirepass
        - $(REDIS_PASSWORD)
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: password
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: switchboard-prod
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

Apply:

```bash
kubectl apply -f redis-deployment.yaml
```

### Step 6: Deploy Backend

Create `backend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: switchboard-prod
spec:
  replicas: 3  # Scale as needed
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/switchboard-backend:latest
        envFrom:
        - configMapRef:
            name: switchboard-config
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: secret-key
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: password
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret-key
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: switchboard-prod
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: switchboard-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

Apply:

```bash
kubectl apply -f backend-deployment.yaml
```

### Step 7: Deploy Frontend

Create `frontend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: switchboard-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/switchboard-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: switchboard-prod
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

Apply:

```bash
kubectl apply -f frontend-deployment.yaml
```

### Step 8: Setup Ingress

Create `ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: switchboard-ingress
  namespace: switchboard-prod
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - orchestrator.example.com
    secretName: switchboard-tls
  rules:
  - host: orchestrator.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      - path: /ws
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

Apply:

```bash
kubectl apply -f ingress.yaml
```

### Step 9: Run Migrations

```bash
# Get backend pod name
POD=$(kubectl get pods -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -it $POD -- alembic upgrade head
```

### Step 10: Monitor Deployment

```bash
# Watch pods
kubectl get pods -w

# Check logs
kubectl logs -f deployment/backend

# Check services
kubectl get svc

# Check ingress
kubectl get ingress
```

---

## Database Setup

### Initial Migration

```bash
# Docker Compose
docker-compose -f docker-compose.phase9.yml exec backend alembic upgrade head

# Kubernetes
kubectl exec -it deployment/backend -- alembic upgrade head
```

### Connection Pooling

Configure in backend:

```python
# backend/app/infrastructure/database.py

# Production pool settings
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,        # Base pool size
    max_overflow=10,     # Additional connections
    pool_timeout=30,     # Connection timeout
    pool_recycle=3600,   # Recycle connections after 1 hour
    pool_pre_ping=True   # Verify connections before use
)
```

### Backup Schedule

Setup automated backups (see Backup & Recovery section).

---

## Environment Configuration

### Production Environment Variables

Complete `.env.production`:

```bash
# ============================================================================
# Core Application
# ============================================================================
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
VERSION=1.0.0

# ============================================================================
# Security
# ============================================================================
SECRET_KEY=<64-char-hex-key>
ALLOWED_HOSTS=["orchestrator.example.com"]
CORS_ORIGINS=["https://orchestrator.example.com"]

# ============================================================================
# Database
# ============================================================================
DATABASE_URL=postgresql+asyncpg://switchboard:PASSWORD@postgres:5432/switchboard_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30

# ============================================================================
# Redis Cache
# ============================================================================
REDIS_URL=redis://:PASSWORD@redis:6379/0
REDIS_MAX_CONNECTIONS=50

# ============================================================================
# JWT Authentication
# ============================================================================
JWT_SECRET_KEY=<128-char-hex-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_ISSUER=orchestrator.example.com

# ============================================================================
# Monitoring
# ============================================================================
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

GRAFANA_ENABLED=true
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=<strong-password>

JAEGER_ENABLED=true
JAEGER_AGENT_HOST=jaeger
JAEGER_AGENT_PORT=6831

# ============================================================================
# Email Alerts
# ============================================================================
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=alerts@example.com
SMTP_PASSWORD=<smtp-password>
SMTP_FROM=alerts@example.com
SMTP_TLS=true

# ============================================================================
# Background Jobs
# ============================================================================
CELERY_BROKER_URL=redis://:PASSWORD@redis:6379/1
CELERY_RESULT_BACKEND=redis://:PASSWORD@redis:6379/2
CELERY_WORKERS=4

# ============================================================================
# Rate Limiting
# ============================================================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=100

# ============================================================================
# Logging
# ============================================================================
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/var/log/switchboard/app.log
```

---

## Security Hardening

### 1. Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Disable Debug Mode

```bash
# In .env.production
DEBUG=false
```

### 3. Strong Passwords

Generate strong passwords for all services:

```bash
openssl rand -base64 32
```

### 4. Restrict Database Access

```bash
# Only allow backend to connect
# In postgresql.conf
listen_addresses = 'localhost, backend'

# In pg_hba.conf
host switchboard_prod switchboard backend md5
```

### 5. Enable HTTPS Only

```nginx
# In nginx config
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### 6. Rate Limiting

```python
# backend/app/middleware/rate_limit.py

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.route("/api")
@limiter.limit("60/minute")
async def api_route():
    pass
```

### 7. Input Validation

All inputs validated with Pydantic (already implemented).

### 8. SQL Injection Prevention

Using SQLAlchemy ORM (already implemented).

### 9. XSS Prevention

```python
# Set security headers
app.add_middleware(
    SecurityHeadersMiddleware,
    content_security_policy="default-src 'self'",
    x_content_type_options="nosniff",
    x_frame_options="SAMEORIGIN"
)
```

---

## SSL/TLS Setup

### Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt-get install certbot

# For nginx
sudo apt-get install python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d orchestrator.example.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Custom Certificate

```nginx
# In nginx config
ssl_certificate /path/to/fullchain.pem;
ssl_certificate_key /path/to/privkey.pem;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
```

---

## Monitoring & Logging

### Prometheus Metrics

Access: `http://localhost:9090`

Key metrics to monitor:
- `http_requests_total` - Request count
- `http_request_duration_seconds` - Request latency
- `agent_operations_total` - Agent operations
- `task_queue_size` - Pending tasks
- `database_connections_active` - DB connections

### Grafana Dashboards

Access: `http://localhost:3001`

Default dashboard: `monitoring/grafana/dashboards/switchboard-main-dashboard.json`

### Application Logs

```bash
# Docker Compose
docker-compose logs -f backend

# Kubernetes
kubectl logs -f deployment/backend
```

### Log Aggregation

Consider using:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Loki** (with Grafana)
- **CloudWatch** (AWS)
- **Stackdriver** (GCP)

---

## Backup & Recovery

See separate `BACKUP_RECOVERY_GUIDE.md` for detailed procedures.

Quick overview:

```bash
# Backup database
./scripts/backup.sh

# Restore database
./scripts/restore.sh backup-2026-02-05.sql.gz
```

---

## Performance Tuning

### Database

```postgresql
-- Increase shared buffers (25% of RAM)
shared_buffers = 4GB

-- Increase work memory
work_mem = 50MB

-- Enable parallel query
max_parallel_workers_per_gather = 4

-- Autovacuum tuning
autovacuum_max_workers = 4
```

### Redis

```redis
# Increase max memory
maxmemory 2gb

# LRU eviction policy
maxmemory-policy allkeys-lru

# Save snapshots
save 900 1
save 300 10
save 60 10000
```

### Application

```python
# Increase worker count
workers = multiprocessing.cpu_count() * 2 + 1

# Enable connection pooling
pool_size = 20
max_overflow = 10
```

---

## Health Checks

### Endpoints

- `/health` - Basic health check
- `/health/db` - Database connectivity
- `/health/redis` - Redis connectivity
- `/metrics` - Prometheus metrics

### Monitoring Script

```bash
#!/bin/bash
# check-health.sh

URL="https://orchestrator.example.com"

# Check main health
if curl -sf "$URL/health" > /dev/null; then
  echo "✓ Application healthy"
else
  echo "✗ Application unhealthy"
  exit 1
fi

# Check database
if curl -sf "$URL/health/db" > /dev/null; then
  echo "✓ Database healthy"
else
  echo "✗ Database unhealthy"
  exit 1
fi

echo "All checks passed"
```

---

## Troubleshooting

### Common Issues

**Issue**: Backend fails to start
```bash
# Check logs
docker-compose logs backend

# Common causes:
# - Database not ready (wait for postgres)
# - Missing environment variables
# - Port already in use
```

**Issue**: Database connection timeout
```bash
# Check database is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U switchboard -d switchboard_prod

# Check connection pooling settings
```

**Issue**: High memory usage
```bash
# Check resource usage
docker stats

# Adjust limits in docker-compose.yml
# Tune database shared_buffers
# Enable Redis maxmemory
```

**Issue**: Slow API responses
```bash
# Check Prometheus metrics
# Look for slow database queries
# Check Redis cache hit ratio
# Review application logs for bottlenecks
```

---

## Support & Maintenance

### Regular Maintenance Tasks

**Daily**:
- Monitor error logs
- Check system metrics
- Verify backups completed

**Weekly**:
- Review performance metrics
- Check disk space
- Update SSL certificates (if needed)

**Monthly**:
- Update dependencies
- Review security alerts
- Test disaster recovery

**Quarterly**:
- Major version updates
- Performance audit
- Security audit

---

## Checklist

### Pre-Deployment

- [ ] Domain configured and DNS propagated
- [ ] SSL certificate obtained
- [ ] Strong passwords generated for all services
- [ ] Environment variables configured
- [ ] Firewall rules configured
- [ ] Monitoring setup (Prometheus + Grafana)
- [ ] Backup strategy defined

### Deployment

- [ ] Services deployed and running
- [ ] Database migrations applied
- [ ] Admin user created
- [ ] Health checks passing
- [ ] SSL/TLS working
- [ ] Monitoring dashboards accessible

### Post-Deployment

- [ ] Load testing completed
- [ ] Backup tested
- [ ] Alerts configured
- [ ] Documentation updated
- [ ] Team trained on operations

---

**Document Version**: 1.0
**Last Updated**: 2026-02-05
**Next Review**: 2026-03-05

**Support**: support@example.com
**Emergency**: oncall@example.com

---

*This guide will be updated as the system evolves.*
