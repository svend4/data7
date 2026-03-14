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

### Tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks` - List all tasks (with filters)
- `GET /api/tasks/{id}` - Get task by ID
- `PUT /api/tasks/{id}/start` - Start task execution
- `PUT /api/tasks/{id}/complete` - Complete task with result
- `PUT /api/tasks/{id}/fail` - Mark task as failed
- `DELETE /api/tasks/{id}` - Delete task
- `GET /api/tasks/stats/summary` - Get task statistics

### Connections
- `POST /api/connections` - Create connection between agents
- `GET /api/connections` - List all connections (with filters)
- `GET /api/connections/{id}` - Get connection by ID
- `PUT /api/connections/{id}/establish` - Establish connection (allocate sockets)
- `PUT /api/connections/{id}/disconnect` - Disconnect connection
- `DELETE /api/connections/{id}` - Delete connection
- `GET /api/connections/stats/summary` - Get connection statistics

### Graphs
- `POST /api/graphs` - Create communication graph
- `GET /api/graphs` - List all graphs
- `GET /api/graphs/{id}` - Get graph by ID
- `POST /api/graphs/{id}/execute` - Start graph execution
- `GET /api/graphs/{id}/executions` - List executions for graph
- `DELETE /api/graphs/{id}` - Delete graph

### Executions
- `GET /api/executions/{id}` - Get execution status
- `PUT /api/executions/{id}/cancel` - Cancel running execution

### System
- `GET /` - Root endpoint with API overview
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

**Phase 1: Core Backend (Week 2-3)**
- ✅ Project structure
- ✅ FastAPI application with CORS
- ✅ Core domain models (Agent, Task, Connection, Graph, Execution)
- ✅ Agent CRUD API (6 endpoints)
- ✅ Task CRUD API (8 endpoints)
- ✅ Connection API (7 endpoints)
- ✅ Graph & Execution API (8 endpoints)
- ✅ In-memory storage (MVP)
- ✅ Statistics endpoints for all resources
- ✅ Socket allocation system (1-100 sockets)
- ⏳ Database persistence (next: PostgreSQL + SQLAlchemy)
- ⏳ WebSocket support (next: real-time updates)
- ⏳ Event sourcing (next: audit trail)

**API Statistics:**
- **29 REST endpoints** across 5 routers
- **4 domain entities** (Agent, Task, Connection, Graph)
- **8 value objects** (Vector3, Color, AgentCapability, etc.)
- **100 switchboard sockets** for connection routing

## Next Steps

1. ✅ ~~Complete REST API~~ → **DONE**
2. **Setup PostgreSQL + SQLAlchemy** (Week 4)
3. **Implement Repository pattern** (Week 4)
4. **Add Alembic migrations** (Week 4)
5. **WebSocket real-time updates** (Week 5-6)
6. **Event sourcing & audit trail** (Week 7)
7. **Authentication & authorization** (Week 8)
