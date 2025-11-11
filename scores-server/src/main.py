"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - runs on startup and shutdown."""
    # Startup: Initialize database
    await init_db()
    yield
    # Shutdown: cleanup if needed


# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    version="1.0.0",
    description="Ultimate Frisbee tournament management and live scoring API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": settings.project_name,
        "version": "1.0.0",
        "docs": "/docs",
    }


# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include routers
from src.routers import seasons, tournaments, matches, teams, players, admin, admin_streamlit
from src.websocket import handlers as ws_handlers

app.include_router(seasons.router, prefix=f"{settings.api_v1_prefix}/seasons", tags=["seasons"])
app.include_router(tournaments.router, prefix=f"{settings.api_v1_prefix}/tournaments", tags=["tournaments"])
app.include_router(matches.router, prefix=f"{settings.api_v1_prefix}/matches", tags=["matches"])
app.include_router(teams.router, prefix=f"{settings.api_v1_prefix}/teams", tags=["teams"])
app.include_router(players.router, prefix=f"{settings.api_v1_prefix}/players", tags=["players"])
app.include_router(admin.router, prefix=f"{settings.api_v1_prefix}/admin", tags=["admin"])
app.include_router(admin_streamlit.router, tags=["admin-ui"])
app.include_router(ws_handlers.router, tags=["websocket"])

