# 🚀 Quick Start Guide - Meta-Orchestrator Switchboard

**Version**: 1.0.0 Production Ready
**Status**: ✅ All phases complete

---

## ⚡ 5-Minute Setup

### 1. Prerequisites
```bash
# Required
- Docker & docker-compose installed
- Git installed
- Ports available: 80, 8000, 3000, 5432, 6379, 9090

# Check Docker
docker --version
docker-compose --version
```

### 2. Clone & Start
```bash
# Clone repository
git clone <repository-url>
cd data7

# Checkout completed branch
git checkout claude/review-habr-article-iDcTr

# Start full stack (15 services)
docker-compose -f docker-compose.phase9.yml up -d

# Watch logs
docker-compose -f docker-compose.phase9.yml logs -f
```

### 3. Wait for Services (30-60 seconds)
```bash
# Check service health
docker-compose -f docker-compose.phase9.yml ps

# All services should be "Up" with healthy status
```

### 4. Access the System

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:80 | - |
| **Backend API** | http://localhost:8000 | - |
| **API Documentation** | http://localhost:8000/api/docs | - |
| **Metrics** | http://localhost:8000/metrics | - |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **Flower (Celery)** | http://localhost:5555 | - |
| **Jaeger (Tracing)** | http://localhost:16686 | - |

---

## 🔐 Test Authentication

### Register New User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "email": "demo@example.com",
    "password": "DemoPass123",
    "full_name": "Demo User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "password": "DemoPass123"
  }'
```

**Response** (save the tokens):
```json
{
  "access_token": "eyJ0eXAi...",
  "refresh_token": "eyJ0eXAi...",
  "token_type": "bearer"
}
```

### Access Protected Endpoint
```bash
# Replace YOUR_ACCESS_TOKEN with the token from login
curl http://localhost:8000/api/agents \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Current User Info
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📊 View Monitoring Dashboards

### Grafana (Recommended)
1. Open: http://localhost:3000
2. Login: **admin** / **admin**
3. Navigate: **Dashboards** → **Meta-Orchestrator Switchboard**
4. View 16 panels with real-time metrics

### Prometheus (Raw Metrics)
1. Open: http://localhost:9090
2. Try queries:
   - `http_requests_total` - Total HTTP requests
   - `http_request_duration_seconds` - Request latency
   - `active_agents` - Active agents count
   - `cache_hit_ratio` - Cache performance

### Jaeger (Distributed Tracing)
1. Open: http://localhost:16686
2. Select service: **switchboard-backend**
3. View traces and spans

### Flower (Celery Monitoring)
1. Open: http://localhost:5555
2. View:
   - Active workers
   - Task queues
   - Task history

---

## 🧪 Run Tests

### Backend Tests
```bash
cd backend

# Install test dependencies
pip install -r requirements-test.txt

# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Run specific test suite
pytest tests/unit/ -v
pytest tests/integration/ -v

# Run load tests
cd tests/load
locust -f locustfile.py --host=http://localhost:8000
```

### Frontend Tests
```bash
cd frontend

# Install dependencies
npm install

# Run unit tests
npm run test

# Run unit tests with coverage
npm run test:coverage

# Run E2E tests (headless)
npm run test:e2e

# Run E2E tests (headed, with browser)
npm run test:e2e:headed

# Run E2E tests (debug mode)
npm run test:e2e:debug
```

---

## 🎨 Frontend Features

### Login to Frontend
1. Open: http://localhost:80
2. Navigate to: **/login**
3. Use demo credentials:
   - Username: **admin**
   - Password: **admin123**
   
   OR register a new account at **/register**

### Available Pages
- `/` - Home/Landing page
- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Main dashboard (protected)
- `/agents` - Agent management (protected)
- `/tasks` - Task management (protected)
- `/analytics` - Analytics dashboard (protected)
- `/alerts` - Alerts management (protected)

### 3D Visualization
- Navigate to the 3D Switchboard view
- See real-time agent status
- Interactive sockets (hover to see details)
- Art Deco aesthetic

---

## 🛠️ Common Operations

### View Logs
```bash
# All services
docker-compose -f docker-compose.phase9.yml logs -f

# Specific service
docker-compose -f docker-compose.phase9.yml logs -f backend
docker-compose -f docker-compose.phase9.yml logs -f frontend
docker-compose -f docker-compose.phase9.yml logs -f db
```

### Restart Services
```bash
# Restart all
docker-compose -f docker-compose.phase9.yml restart

# Restart specific service
docker-compose -f docker-compose.phase9.yml restart backend
```

### Stop Services
```bash
# Stop all
docker-compose -f docker-compose.phase9.yml down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose -f docker-compose.phase9.yml down -v
```

### Shell Access
```bash
# Backend shell
docker-compose -f docker-compose.phase9.yml exec backend bash

# Database shell
docker-compose -f docker-compose.phase9.yml exec db psql -U switchboard

# Redis CLI
docker-compose -f docker-compose.phase9.yml exec redis redis-cli
```

---

## 📖 Next Steps

### Explore Documentation
- `PROJECT_COMPLETE_SUMMARY.md` - Full project overview
- `PHASE9_ADVANCED_GUIDE.md` - Phase 9 features guide
- `DEPLOYMENT_GUIDE.md` - Production deployment
- `backend/tests/README.md` - Testing guide
- `frontend/e2e/README.md` - E2E testing guide

### Try API Endpoints
Visit: http://localhost:8000/api/docs

Explore all available endpoints:
- `/api/agents` - Agent management
- `/api/tasks` - Task management
- `/api/graphs` - Graph management
- `/api/optimization` - Graph optimization
- `/api/analytics` - System analytics
- `/api/alerts` - Alert management
- `/api/reports` - Report generation
- `/api/auth/*` - Authentication

### Monitor System
- Check Grafana dashboards for metrics
- View Prometheus alerts
- Analyze traces in Jaeger
- Monitor Celery tasks in Flower

---

## 🐛 Troubleshooting

### Services Won't Start
```bash
# Check if ports are available
netstat -an | grep -E "80|8000|3000|5432|6379|9090"

# Check Docker resources
docker system df
docker system prune  # Clean up if needed

# View service logs for errors
docker-compose -f docker-compose.phase9.yml logs
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.phase9.yml ps db

# Check database logs
docker-compose -f docker-compose.phase9.yml logs db

# Connect to database
docker-compose -f docker-compose.phase9.yml exec db psql -U switchboard -d switchboard
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose -f docker-compose.phase9.yml ps redis

# Test Redis connection
docker-compose -f docker-compose.phase9.yml exec redis redis-cli ping
# Should return: PONG
```

### Authentication Not Working
```bash
# Check backend logs
docker-compose -f docker-compose.phase9.yml logs backend | grep auth

# Verify JWT secret is set
docker-compose -f docker-compose.phase9.yml exec backend env | grep SECRET_KEY

# Test auth endpoints directly
curl http://localhost:8000/api/auth/health
```

---

## 💡 Tips

1. **First Time Setup**: Wait 60 seconds after `docker-compose up` for all services to initialize
2. **Cache Issues**: Clear browser cache if frontend behaves unexpectedly
3. **Token Expiry**: Access tokens expire after 15 minutes, use refresh token
4. **Monitoring**: Keep Grafana dashboard open to see real-time system health
5. **Development**: Use `docker-compose logs -f backend` during development

---

## ✅ Health Check

Run this to verify everything is working:

```bash
# Check all services
curl http://localhost:8000/health
curl http://localhost:8000/api/auth/health
curl http://localhost:3000/api/health

# Check metrics
curl http://localhost:8000/metrics | head -20

# Expected: All return 200 OK with "healthy" status
```

---

## 🎉 You're Ready!

The Meta-Orchestrator Switchboard is now running with:

✅ 15 services active
✅ Full authentication system
✅ Real-time monitoring
✅ Background job processing
✅ 3D visualization
✅ Complete API

**Enjoy exploring the system!** 🎭

---

**Need help?** Check the documentation or view logs for troubleshooting.
