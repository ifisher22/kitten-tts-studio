"""
TTS Router - Text-to-Speech endpoints
"""
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from typing import Optional

from app.models.schemas import (
    TTSRequest,
    TTSResponse,
    VoicesResponse,
    VoiceInfo,
    ModelsResponse,
    ModelInfo,
)
from app.services.tts_service import tts_service


router = APIRouter(prefix="/tts", tags=["Text-to-Speech"])


@router.post("/generate", response_model=TTSResponse)
async def generate_speech(request: TTSRequest):
    """
    Generate speech from text
    
    Returns audio as streaming WAV file
    """
    # Generate speech
    audio_bytes = tts_service.generate_speech(
        text=request.text,
        voice=request.voice or "Jasper",
        speed=request.speed or 1.0,
        model=request.model,
    )
    
    if audio_bytes is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate speech"
        )
    
    # Return streaming response
    return StreamingResponse(
        iter([audio_bytes]),
        media_type="audio/wav",
        headers={
            "Content-Disposition": "attachment; filename=speech.wav",
            "X-Voice-Used": request.voice or "Jasper",
            "X-Text-Length": str(len(request.text)),
            "X-Model-Used": tts_service.active_model,
        }
    )


@router.post("/stream")
async def stream_speech(request: TTSRequest):
    """
    Stream speech audio directly
    
    This endpoint returns raw audio bytes for direct playback
    """
    # Generate speech
    audio_bytes = tts_service.generate_speech(
        text=request.text,
        voice=request.voice or "Jasper",
        speed=request.speed or 1.0,
        model=request.model,
    )
    
    if audio_bytes is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate speech"
        )
    
    # Return streaming response with audio/wav content type
    return StreamingResponse(
        iter([audio_bytes]),
        media_type="audio/wav",
        headers={
            "Content-Disposition": "inline; filename=speech.wav",
            "Accept-Ranges": "bytes",
            "Content-Length": str(len(audio_bytes))
        }
    )


@router.get("/voices", response_model=VoicesResponse)
async def list_voices(model: Optional[str] = Query(default=None)):
    """Get list of available voices"""
    mapping = tts_service.get_available_voice_mapping(model)
    voices = []
    for name, internal in mapping.items():
        gender = tts_service.get_voice_gender(name, model)
        voices.append(VoiceInfo(
            name=name,
            alias=internal,
            gender=gender
        ))
    
    return VoicesResponse(voices=voices)


@router.get("/models", response_model=ModelsResponse)
async def list_models():
    """Get list of available models"""
    models = []
    for model_key in tts_service.available_models:
        models.append(
            ModelInfo(
                key=model_key,
                label=tts_service.model_labels.get(model_key, model_key),
                loaded=tts_service.is_model_loaded(model_key),
            )
        )

    return ModelsResponse(models=models, active_model=tts_service.active_model)
