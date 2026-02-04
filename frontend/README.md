# Meta-Orchestrator Switchboard - Frontend

**Art Deco 1920s Telephonic Exchange for Multi-Agent AI Systems**

React + TypeScript + Vite frontend for the switchboard meta-orchestration system.

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env if your backend is not on localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at: http://localhost:5173

### 4. Build for Production

```bash
npm run build
npm run preview  # Preview production build
```

## Features

### Current (Phase 0 - MVP)
- ✅ Agent Registry - View all registered agents
- ✅ Agent Statistics Dashboard - Real-time stats
- ✅ Create Agent - Register new agents with capabilities
- ✅ Delete Agent - Remove agents from system
- ✅ Art Deco UI Theme - 1920s telephonic exchange aesthetic
- ✅ Real-time Updates - Auto-refresh every 3-5 seconds

### Planned (Future Phases)
- ⏳ Task Management - Create and assign tasks
- ⏳ Connection Viewer - See agent connections
- ⏳ Communication Graph - Visualize task flows
- ⏳ 3D Switchboard View - Three.js visualization
- ⏳ WebSocket Real-time - Live updates via WebSocket
- ⏳ MMO-style Interface - Immersive 3D experience

## Architecture

```
frontend/
├── src/
│   ├── components/      # React components
│   │   ├── AgentRegistry.tsx
│   │   ├── AgentCard.tsx
│   │   ├── CreateAgentModal.tsx
│   │   └── SwitchboardStats.tsx
│   ├── services/        # API services
│   │   └── api.ts
│   ├── types/           # TypeScript types
│   │   └── index.ts
│   ├── App.tsx          # Main app component
│   └── main.tsx         # Entry point
├── public/              # Static assets
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Technology Stack

- **Framework**: React 18.2
- **Build Tool**: Vite 5.0
- **Language**: TypeScript 5.3
- **State Management**: Zustand 4.5
- **Data Fetching**: TanStack Query (React Query) 5.17
- **HTTP Client**: Axios 1.6
- **3D Graphics**: Three.js 0.160 + React Three Fiber (future)
- **Animation**: Framer Motion 11.0
- **Styling**: CSS3 (Art Deco theme)

## Art Deco Theme

### Color Palette
- **Gold**: #D4AF37 - Primary accent, highlights
- **Bronze**: #CD7F32 - Secondary accent, borders
- **Black**: #141414 - Primary background
- **Cream**: #FFFDD0 - Primary text
- **Dark Gray**: #2a2a2a - Secondary background

### Typography
- **Font**: Georgia, Times New Roman (serif)
- **Letter Spacing**: 0.05-0.1em for elegance
- **Uppercase**: For labels and section titles

### Visual Style
- Geometric borders and frames
- Symmetrical layouts
- Gold/bronze accents
- 1920s telephone exchange aesthetic

## Development

### Linting
```bash
npm run lint
```

### Type Checking
```bash
npm run type-check
```

### Code Structure
- Use TypeScript for all components
- Props interfaces defined inline or in types/
- CSS modules for component styles
- React Query for server state
- Zustand for client state (future)

## API Integration

The frontend connects to the FastAPI backend on `localhost:8000`. All API calls go through the `apiService` in `src/services/api.ts`.

### Available Endpoints
- `GET /api/agents` - List agents
- `POST /api/agents` - Create agent
- `GET /api/agents/{id}` - Get agent
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent
- `GET /api/agents/stats/summary` - Get statistics

## Current Status

**Phase 0: Foundation (MVP)** - In Progress
- ✅ Project setup
- ✅ Art Deco theme implementation
- ✅ Agent Registry UI
- ✅ Agent CRUD operations
- ✅ Statistics dashboard
- ✅ Real-time updates (polling)
- ⏳ WebSocket integration (pending)
- ⏳ 3D visualization (pending)

## Next Steps

1. Add Task management UI
2. Implement Connection visualization
3. Create Communication Graph viewer
4. Integrate WebSocket for real-time updates
5. Build 3D switchboard scene with Three.js
6. Add authentication & user management
