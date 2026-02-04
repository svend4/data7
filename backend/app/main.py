"""
FastAPI Main Application
Art Deco Switchboard API - Entry Point
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.agents import router as agents_router
from app.api.tasks import router as tasks_router
from app.api.connections import router as connections_router
from app.api.graphs import router as graphs_router, executions_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events"""
    # Startup
    setup_logging()
    print("🎭 Art Deco Switchboard System Starting...")
    print(f"📞 Version: {settings.VERSION}")
    print(f"🌐 Environment: {settings.ENVIRONMENT}")

    yield

    # Shutdown
    print("🎭 Shutting down gracefully...")


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

# Register routers
app.include_router(agents_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(connections_router, prefix="/api")
app.include_router(graphs_router, prefix="/api")
app.include_router(executions_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Meta-Orchestrator Switchboard",
        "version": settings.VERSION,
        "status": "operational",
        "theme": "Art Deco 1920s Telephonic Exchange",
        "endpoints": {
            "docs": "/api/docs",
            "agents": "/api/agents",
            "tasks": "/api/tasks",
            "connections": "/api/connections",
            "graphs": "/api/graphs",
            "executions": "/api/executions",
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
