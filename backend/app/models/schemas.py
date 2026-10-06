"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class TTSRequest(BaseModel):
    """Text-to-Speech request schema"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Text to convert to speech",
        examples=["Hello, this is a test of the Kitten TTS system."]
    )
    voice: Optional[str] = Field(
        default="Jasper",
        description="Voice to use for synthesis",
        examples=["Bella", "Jasper", "Luna", "Bruno", "Rosie", "Hugo", "Kiki", "Leo"]
    )
    speed: Optional[float] = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Speech speed multiplier (0.5 = slow, 2.0 = fast)"
    )
    model: Optional[Literal["kitten-tts-mini-0.8", "kitten-tts-nano-0.2"]] = Field(
        default="kitten-tts-mini-0.8",
        description="TTS model to use for synthesis"
    )


class TTSResponse(BaseModel):
    """Text-to-Speech response metadata"""
    success: bool
    message: str
    voice_used: str
    text_length: int
    audio_duration_estimate: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    available_voices: list[str]
    available_models: list[str]
    active_model: str
    version: str


class VoiceInfo(BaseModel):
    """Voice information"""
    name: str
    alias: str
    gender: str


class VoicesResponse(BaseModel):
    """Available voices response"""
    voices: list[VoiceInfo]


class ModelInfo(BaseModel):
    """Model information"""
    key: str
    label: str
    loaded: bool


class ModelsResponse(BaseModel):
    """Available models response"""
    models: list[ModelInfo]
    active_model: str
