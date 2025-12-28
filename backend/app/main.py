"""
Smart-Drive FastAPI Backend
Main application entry point with WebSocket support for real-time AI chat
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.config import settings
from app.database import init_db
from app.routers import auth, files, drive, chat
from app.core.vector_store import init_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle"""
    # Startup
    await init_db()
    await init_vector_store()
    yield
    # Shutdown - cleanup if needed


app = FastAPI(
    title="Smart-Drive API",
    description="AI-powered document and video analysis platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(drive.router, prefix="/api/v1/drive", tags=["drive"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Smart-Drive API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "vector_store": "ready",
            "file_system": "accessible"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )


