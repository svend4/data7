# Meta-Orchestrator Switchboard - Backend

**Art Deco 1920s Telephonic Exchange for Multi-Agent AI Systems**

FastAPI-based backend for the switchboard meta-orchestration system.

## Quick Start

### 1. Setup Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Development Server

```bash
python -m app.main
```

Or with uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## API Endpoints

### Agents
- `POST /api/agents` - Create new agent
- `GET /api/agents` - List all agents
- `GET /api/agents/{id}` - Get agent by ID
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent
- `GET /api/agents/stats/summary` - Get agent statistics

### Health
- `GET /` - Root endpoint
- `GET /health` - Health check

## Architecture

```
backend/
├── app/
│   ├── api/          # API endpoints (routers)
│   ├── core/         # Core config and utilities
│   ├── domain/       # Domain models (entities, value objects)
│   ├── infrastructure/  # Database, external services
│   ├── schemas/      # Pydantic API schemas
│   └── main.py       # Application entry point
├── tests/            # Test suite
├── requirements.txt  # Python dependencies
└── .env.example      # Environment template
```

## Development

### Run Tests
```bash
pytest
```

### Code Quality
```bash
# Format
black app/

# Lint
ruff app/

# Type check
mypy app/
```

## Technology Stack

- **Framework**: FastAPI 0.109
- **Async**: asyncio, uvicorn
- **Validation**: Pydantic 2.5
- **Database**: PostgreSQL + SQLAlchemy (future)
- **Cache**: Redis (future)
- **WebSocket**: python-socketio (future)

## Current Status

**Phase 0: Foundation (MVP)**
- ✅ Project structure
- ✅ FastAPI application
- ✅ Core domain models (Agent, Task, Connection)
- ✅ Agent CRUD API
- 🔄 In-memory storage (will migrate to PostgreSQL)
- ⏳ Task API (pending)
- ⏳ Connection API (pending)
- ⏳ WebSocket support (pending)

## Next Steps

1. Add Task and Connection endpoints
2. Implement database persistence (PostgreSQL)
3. Add WebSocket support for real-time updates
4. Implement GraphExecution logic
5. Add authentication & authorization
