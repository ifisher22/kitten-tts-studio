"""
Kitten TTS API - FastAPI Application Entry Point

A production-ready Text-to-Speech API using Kitten TTS local models
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.routers import health, tts
from app.services.tts_service import tts_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler
    Loads TTS model on startup and cleans up on shutdown
    """
    # Startup
    logger.info("=" * 50)
    logger.info("Starting Kitten TTS API Server")
    logger.info("=" * 50)
    
    logger.info("Loading TTS model...")
    success = tts_service.load_model()
    
    if success:
        logger.info(f"✓ Available voices: {', '.join(tts_service.available_voices)}")
        logger.info("✓ Server ready!")
    else:
        logger.error("✗ Failed to load model - service will not function properly")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Kitten TTS API Server...")


# Create FastAPI app
app = FastAPI(
    title="Kitten TTS API",
    description="""
    Production-ready Text-to-Speech API using local Kitten TTS models.
    
    Features:
    - 8 different voices (male and female)
    - Adjustable speech speed
    - WAV audio output
    - CPU-optimized inference
    - Runtime model switching (mini/nano)
    """,
    version="0.8.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add middleware
# CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(health.router)
app.include_router(tts.router)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8008,
        reload=False,
        workers=1,
        log_level="info"
    )
