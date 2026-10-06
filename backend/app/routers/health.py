"""
Health Router - Health check endpoints
"""
from fastapi import APIRouter

from app.models.schemas import HealthResponse
from app.services.tts_service import tts_service


router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns service status and model information
    """
    return HealthResponse(
        status="healthy",
        model_loaded=tts_service.is_loaded,
        available_voices=tts_service.available_voices,
        available_models=tts_service.available_models,
        active_model=tts_service.active_model,
        version="0.8.0"
    )


@router.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Kitten TTS API",
        "version": "0.8.0",
        "description": "Text-to-Speech API using local Kitten TTS models",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "voices": "/tts/voices",
            "models": "/tts/models",
            "generate": "POST /tts/generate",
            "stream": "POST /tts/stream"
        }
    }
