"""
FastAPI Main Application
Art Deco Switchboard API - Entry Point

Phase 9 Integration:
- Prometheus metrics middleware
- JWT authentication
- Redis caching
- WebSocket real-time updates
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.infrastructure import init_database, close_database
from app.api.agents import router as agents_router
from app.api.tasks import router as tasks_router
from app.api.connections import router as connections_router
from app.api.graphs import router as graphs_router, executions_router
from app.api.optimization import router as optimization_router
from app.api.analytics import router as analytics_router
from app.api.alerts import router as alerts_router
from app.api.reports import router as reports_router
from app.api.websocket import router as websocket_router

# Phase 9: Advanced features
from app.middleware.prometheus import PrometheusMiddleware, metrics_endpoint
from app.cache.redis import init_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events"""
    # Startup
    setup_logging()
    print("🎭 Art Deco Switchboard System Starting...")
    print(f"📞 Version: {settings.VERSION}")
    print(f"🌐 Environment: {settings.ENVIRONMENT}")

    # Initialize database
    await init_database()
    print("✅ Database initialized")

    # Phase 9: Initialize Redis cache
    try:
        await init_redis()
        print("✅ Redis cache initialized")
    except Exception as e:
        print(f"⚠️  Redis cache initialization failed: {e}")
        print("   Continuing without cache...")

    print("✅ Switchboard system ready!")

    yield

    # Shutdown
    print("🎭 Shutting down gracefully...")

    # Close Redis
    try:
        await close_redis()
        print("✅ Redis connections closed")
    except Exception:
        pass

    # Close database
    await close_database()
    print("✅ Database connections closed")
    print("👋 Goodbye!")


app = FastAPI(
    title="Meta-Orchestrator Switchboard API",
    description="Art Deco 1920s Telephonic Exchange for Multi-Agent AI Systems",
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 9: Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)

# Register routers
app.include_router(agents_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(connections_router, prefix="/api")
app.include_router(graphs_router, prefix="/api")
app.include_router(executions_router, prefix="/api")
app.include_router(optimization_router)  # Optimization API (includes /api in router)
app.include_router(analytics_router)  # Analytics API (includes /api in router)
app.include_router(alerts_router)  # Alerts API (includes /api in router)
app.include_router(reports_router)  # Reports API (includes /api in router)
app.include_router(websocket_router)  # WebSocket has no /api prefix


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Meta-Orchestrator Switchboard",
        "version": settings.VERSION,
        "status": "operational",
        "theme": "Art Deco 1920s Telephonic Exchange",
        "phase": "Phase 9 - Advanced Features",
        "features": {
            "authentication": "JWT with RBAC",
            "caching": "Redis multi-layer",
            "monitoring": "Prometheus + Grafana",
            "real_time": "WebSocket updates",
            "background_jobs": "Celery workers"
        },
        "endpoints": {
            "docs": "/api/docs",
            "health": "/health",
            "metrics": "/metrics",
            "auth": "/api/auth/*",
            "agents": "/api/agents",
            "tasks": "/api/tasks",
            "connections": "/api/connections",
            "graphs": "/api/graphs",
            "executions": "/api/executions",
            "optimization": "/api/optimization",
            "analytics": "/api/analytics",
            "alerts": "/api/alerts",
            "reports": "/api/reports",
            "websocket": "/ws/events",
            "websocket_stats": "/ws/stats",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "switchboard-api",
            "version": settings.VERSION,
        }
    )


# Phase 9: Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return metrics_endpoint()


# Phase 9: Authentication routes
from app.api.auth import router as auth_router
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
