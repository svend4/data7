# Meta-Orchestrator Switchboard - MVP

**Art Deco 1920s Telephonic Exchange for Multi-Agent AI Systems**

![Status](https://img.shields.io/badge/Status-MVP%20Development-yellow)
![Version](https://img.shields.io/badge/Version-0.1.0-blue)
![License](https://img.shields.io/badge/License-Private-red)

## 🎭 Overview

A meta-orchestration system for coordinating multiple AI agents using the metaphor of a 1920s telephone switchboard. Operators (diffusion models) connect agents through a visual, Art Deco-themed interface.

**Complexity Level**: 3.5 (~70-80 on 1-1000 scale)
**Technology Readiness Level**: 2.5 (Proof of Concept)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                  │
│              Art Deco UI • Agent Registry • Stats           │
│                    http://localhost:5173                    │
└────────────────────┬────────────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────────────┐
│                  Backend (FastAPI)                          │
│         Agent Management • Task Routing • Events            │
│                    http://localhost:8000                    │
└────────────────────┬────────────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
┌─────▼─────┐  ┌────▼─────┐  ┌────▼─────┐
│PostgreSQL │  │  Redis   │  │ WebSocket│
│ (future)  │  │ (future) │  │ (future) │
└───────────┘  └──────────┘  └──────────┘
```

## 📁 Project Structure

```
data7/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # REST endpoints
│   │   ├── core/           # Config, logging
│   │   ├── domain/         # Business logic (entities, value objects)
│   │   ├── infrastructure/ # DB, external services
│   │   ├── schemas/        # Pydantic models
│   │   └── main.py         # Application entry
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── services/       # API client
│   │   ├── types/          # TypeScript definitions
│   │   └── App.tsx         # Main component
│   ├── public/             # Static assets
│   └── package.json        # Node dependencies
│
├── docs/                   # Documentation
│   ├── api/                # API specs
│   ├── architecture/       # System design
│   └── guides/             # User guides
│
├── docker/                 # Docker configurations
├── scripts/                # Utility scripts
│
└── TECHNICAL_SPEC_*        # Complete technical specifications
    ├── PART1_UML.md        # Domain models (Levels 1-3)
    ├── PART2_UML.md        # Advanced models (Levels 4-5)
    ├── PART3_API.md        # REST API specs
    ├── PART4_SCHEMAS.md    # Data schemas
    ├── PART5_SCHEMAS_EVENTS.md  # Events & WebSocket
    ├── PART6_VISUALIZATION.md   # UI mockups
    ├── PART7_VISUALIZATION_3D.md # 3D scenes
    └── PART8_ROADMAP.md    # 32-week plan
```

## 🚀 Quick Start

### Prerequisites

- **Backend**: Python 3.11+, pip
- **Frontend**: Node.js 18+, npm
- **Database** (future): PostgreSQL 15+, Redis 7+

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Run development server
python -m app.main
```

Backend will be available at: **http://localhost:8000**

API Docs: **http://localhost:8000/api/docs**

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure
cp .env.example .env

# Run development server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

### 3. Access the Application

1. Open browser: http://localhost:5173
2. You should see the Art Deco switchboard interface
3. Click "Register New Agent" to create your first agent
4. View real-time statistics in the dashboard

## 🎨 Features

### ✅ Current (Phase 0 - MVP Foundation)

**Backend:**
- FastAPI REST API with OpenAPI docs
- Domain models: Agent, Task, Connection, CommunicationGraph
- Value objects: Vector3, Color, Capabilities, Metrics
- Agent CRUD endpoints
- Statistics aggregation
- In-memory storage (temporary)

**Frontend:**
- React + TypeScript + Vite
- Art Deco 1920s theme (Gold #D4AF37, Bronze #CD7F32)
- Agent Registry - View all agents
- Agent Statistics - Real-time dashboard
- Create Agent Modal - Register with capabilities
- Real-time updates (3-5s polling)
- Responsive grid layout

### ⏳ Planned (Future Phases)

**Phase 1 (Weeks 3-8): Core Backend**
- PostgreSQL database integration
- Task management endpoints
- Connection routing logic
- Event sourcing system
- WebSocket server

**Phase 2 (Weeks 9-14): Web Frontend**
- Task assignment UI
- Connection visualization (2D)
- Graph execution viewer
- WebSocket real-time updates

**Phase 3 (Weeks 15-22): 3D MMO**
- Three.js switchboard scene
- Art Deco operator character
- Wire physics animations
- Immersive camera controls
- VFX particles and lighting

**Phase 4+ (Weeks 23-32)**
- Diffusion LLM integration
- Advanced scheduling
- Multi-tenancy
- Production deployment

## 📊 Current Status

**Overall Progress**: 15% complete (MVP foundation)
**TRL Level**: 2.5 (Proof of Concept)

| Component | Status | Progress |
|-----------|--------|----------|
| Project Structure | ✅ Complete | 100% |
| Backend Core | ✅ Complete | 100% |
| Frontend Core | ✅ Complete | 100% |
| API Endpoints | 🔄 Partial | 40% |
| Database | ⏳ Pending | 0% |
| WebSocket | ⏳ Pending | 0% |
| 3D Visualization | ⏳ Pending | 0% |

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.109
- **Language**: Python 3.11+
- **Validation**: Pydantic 2.5
- **ASGI Server**: Uvicorn
- **Database**: PostgreSQL + SQLAlchemy (planned)
- **Cache**: Redis (planned)
- **WebSocket**: python-socketio (planned)

### Frontend
- **Framework**: React 18.2
- **Language**: TypeScript 5.3
- **Build**: Vite 5.0
- **State**: TanStack Query 5.17, Zustand 4.5
- **HTTP**: Axios 1.6
- **3D**: Three.js 0.160 + React Three Fiber (planned)
- **Animation**: Framer Motion 11.0

### DevOps (Planned)
- **Containers**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack

## 📖 Documentation

- **API Documentation**: [TECHNICAL_SPEC_PART3_API.md](./TECHNICAL_SPEC_PART3_API.md)
- **Data Schemas**: [TECHNICAL_SPEC_PART4_SCHEMAS.md](./TECHNICAL_SPEC_PART4_SCHEMAS.md)
- **Implementation Roadmap**: [TECHNICAL_SPEC_PART8_ROADMAP.md](./TECHNICAL_SPEC_PART8_ROADMAP.md)
- **Complete Summary**: [OPTION_A_COMPLETE_SUMMARY.md](./OPTION_A_COMPLETE_SUMMARY.md)

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm run test
npm run type-check
```

## 📝 API Examples

### Create an Agent

```bash
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Budget Analyst",
    "capabilities": [
      {
        "name": "financial_analysis",
        "category": "analysis",
        "level": 4
      }
    ]
  }'
```

### List All Agents

```bash
curl http://localhost:8000/api/agents
```

### Get Statistics

```bash
curl http://localhost:8000/api/agents/stats/summary
```

## 🎯 Next Steps

1. **Complete Agent API** - Add remaining endpoints
2. **Task Management** - Implement task CRUD
3. **Database Migration** - PostgreSQL integration
4. **WebSocket Setup** - Real-time updates
5. **3D Prototype** - Basic Three.js scene
6. **Testing Suite** - Comprehensive tests

## 📅 Timeline

- **Week 1-2** (Current): ✅ Foundation & MVP
- **Week 3-8**: Core backend + database
- **Week 9-14**: Web UI completion
- **Week 15-22**: 3D visualization
- **Week 23-32**: Advanced features + launch

## 👥 Team Requirements

- **Backend**: 2 Python/FastAPI developers
- **Frontend**: 2 React/TypeScript developers
- **3D Graphics**: 1 Three.js specialist
- **DevOps**: 1 infrastructure engineer

**Total**: 6-8 people
**Budget**: ~$648K (32 weeks)

## 📄 License

Private - Internal Development

---

**Version**: 0.1.0
**Last Updated**: 2026-02-04
**Phase**: 0 (MVP Foundation)
**Status**: 🟢 Active Development
