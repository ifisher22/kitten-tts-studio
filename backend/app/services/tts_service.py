"""
TTS Service - Handles model loading and inference
"""
import io
import os
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

import numpy as np
import soundfile as sf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Fix for espeakng-loader / phonemizer compatibility issue
def _setup_espeak():
    """Setup espeak-ng paths for Windows compatibility"""
    try:
        import espeakng_loader
        from phonemizer.backend.espeak.wrapper import EspeakWrapper

        lib_path = espeakng_loader.get_library_path()
        data_path = espeakng_loader.get_data_path()

        # Ensure DLL folder is visible on Windows.
        try:
            espeakng_loader.make_library_available()
        except Exception as dll_err:
            logger.debug(f"espeak-ng DLL path setup warning: {dll_err}")

        # Ensure both phonemizer and native espeak can find library/data.
        os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = lib_path
        os.environ["ESPEAK_DATA_PATH"] = data_path

        # Keep wrapper in sync with explicit library path.
        EspeakWrapper.set_library(lib_path)

        logger.info(f"espeak-ng library path: {lib_path}")
        logger.info(f"espeak-ng data path: {data_path}")

        # Backward-compatible no-op for misaki versions that call set_data_path.
        if not hasattr(EspeakWrapper, "set_data_path"):
            @classmethod
            def set_data_path(cls, path):
                os.environ["ESPEAK_DATA_PATH"] = str(path)

            EspeakWrapper.set_data_path = set_data_path

        logger.info("espeak setup complete")
    except Exception as e:
        logger.warning(f"espeak setup warning: {e}")


# Run setup before importing kittentts
_setup_espeak()


class TTSService:
    """Singleton service for TTS model management"""

    _instance: Optional["TTSService"] = None
    _models: Dict[str, Any] = {}
    _model_paths: Dict[str, str] = {}
    _active_model_key: str = "kitten-tts-mini-0.8"
    _available_voices: Dict[str, str] = {}
    _model_voice_mappings: Dict[str, Dict[str, str]] = {}

    MODEL_SPECS = {
        "kitten-tts-mini-0.8": {
            "local_dir": "KittenML_kitten-tts-mini-0.8",
            "label": "Kitten TTS Mini 0.8",
        },
        "kitten-tts-nano-0.2": {
            "local_dir": "KittenML_kitten-tts-nano-0.2",
            "label": "Kitten TTS Nano 0.2",
        },
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TTSService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._model_paths:
            self._model_paths = self._resolve_local_model_paths()
            logger.info(f"Resolved local model paths: {self._model_paths}")

    def _resolve_local_model_paths(self) -> Dict[str, str]:
        """Resolve local model directory paths from project root/model."""
        project_root = Path(__file__).resolve().parents[3]
        model_root = project_root / "model"
        resolved: Dict[str, str] = {}

        for model_key, spec in self.MODEL_SPECS.items():
            model_path = model_root / spec["local_dir"]
            resolved[model_key] = str(model_path)
            if not model_path.exists():
                logger.warning(f"Model path does not exist for {model_key}: {model_path}")

        return resolved

    def _normalize_model_key(self, model_key: Optional[str]) -> str:
        """Normalize requested model key with safe fallback."""
        if model_key in self.MODEL_SPECS:
            return model_key
        if model_key:
            logger.warning(
                f"Unknown model '{model_key}', using default '{self._active_model_key}'"
            )
        return self._active_model_key

    def load_model(self, model_key: Optional[str] = None) -> bool:
        """
        Load a Kitten TTS model.

        Returns:
            bool: True if model loaded successfully
        """
        target_model = self._normalize_model_key(model_key)

        if target_model in self._models:
            self._active_model_key = target_model
            return True

        try:
            logger.info(f"Loading Kitten TTS model: {target_model}")

            model_path = self._model_paths.get(target_model, "")
            if not model_path or not os.path.isdir(model_path):
                logger.error(f"Local model directory not found: {model_path}")
                return False

            self._models[target_model], config = self._load_local_model(model_path)
            self._model_voice_mappings[target_model] = self._build_voice_mapping_for_model(
                self._models[target_model], config
            )
            self._active_model_key = target_model
            self._available_voices = self._model_voice_mappings[target_model]
            logger.info(f"Model loaded successfully (CPU mode): {target_model}")

            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return False

    def _load_local_model(self, model_dir: str):
        """Load local Kitten model from config.json and model files."""
        from kittentts.onnx_model import KittenTTS_1_Onnx

        model_root = Path(model_dir)
        config_path = model_root / "config.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Missing config file: {config_path}")

        with config_path.open("r", encoding="utf-8") as f:
            config = json.load(f)

        model_file = config.get("model_file")
        voices_file = config.get("voices")
        if not model_file or not voices_file:
            raise ValueError(f"Invalid config in {config_path}: missing model_file/voices")

        onnx_path = model_root / model_file
        voices_path = model_root / voices_file
        if not onnx_path.exists():
            raise FileNotFoundError(f"Missing ONNX file: {onnx_path}")
        if not voices_path.exists():
            raise FileNotFoundError(f"Missing voices file: {voices_path}")

        model = KittenTTS_1_Onnx(
            model_path=str(onnx_path),
            voices_path=str(voices_path),
            speed_priors=config.get("speed_priors", {}),
            voice_aliases=config.get("voice_aliases", {}),
        )
        return model, config

    def _build_voice_mapping_for_model(self, model_instance: Any, config: Dict[str, Any]) -> Dict[str, str]:
        """Build voice display->internal mapping for a specific model."""
        alias_map = config.get("voice_aliases", {}) or {}
        internal_voices = list(getattr(model_instance, "available_voices", []) or [])

        # Mini models expose friendly names via voice_aliases; nano usually has none.
        if alias_map:
            return {name: internal for name, internal in alias_map.items()}

        # Fallback to internal IDs as both display name and actual value.
        return {voice: voice for voice in internal_voices}

    @property
    def is_loaded(self) -> bool:
        """Check if active model is loaded"""
        return self._active_model_key in self._models

    @property
    def active_model(self) -> str:
        """Get active model key."""
        return self._active_model_key

    @property
    def available_models(self) -> List[str]:
        """Get all available model keys."""
        return list(self.MODEL_SPECS.keys())

    @property
    def model_labels(self) -> Dict[str, str]:
        """Get model display labels by key."""
        return {key: spec["label"] for key, spec in self.MODEL_SPECS.items()}

    def is_model_loaded(self, model_key: str) -> bool:
        """Check if target model has already been loaded."""
        return model_key in self._models

    @property
    def available_voices(self) -> List[str]:
        """Get list of available voice names"""
        return list(self._available_voices.keys())

    def get_available_voice_mapping(self, model_key: Optional[str] = None) -> Dict[str, str]:
        """Get voice display->internal mapping for a model."""
        target_model = self._normalize_model_key(model_key)
        if target_model not in self._models:
            if not self.load_model(target_model):
                return {}
        return self._model_voice_mappings.get(target_model, {})

    def get_voice_gender(self, voice_name: str, model_key: Optional[str] = None) -> str:
        """Get voice gender based on name suffix"""
        mapping = self.get_available_voice_mapping(model_key)
        internal = mapping.get(voice_name, voice_name)
        if internal.endswith("-f"):
            return "female"
        if internal.endswith("-m"):
            return "male"
        return "unknown"

    def generate_speech(
        self,
        text: str,
        voice: str = "Jasper",
        speed: float = 1.0,
        model: Optional[str] = None,
    ) -> Optional[bytes]:
        """
        Generate speech from text.

        Args:
            text: Text to synthesize
            voice: Voice name to use
            speed: Speed multiplier (0.5-2.0)
            model: Model key to use

        Returns:
            WAV audio bytes or None on failure
        """
        try:
            model_key = self._normalize_model_key(model)
            if not self.is_model_loaded(model_key):
                if not self.load_model(model_key):
                    logger.error(f"Model not loaded: {model_key}")
                    return None

            self._active_model_key = model_key
            model_instance = self._models[model_key]
            self._available_voices = self._model_voice_mappings.get(model_key, {})

            # Validate and map voice name
            voice_mapping = self._model_voice_mappings.get(model_key, {})
            if voice not in voice_mapping:
                logger.warning(f"Unknown voice '{voice}', using default 'Jasper'")
                voice = next(iter(voice_mapping.keys()), "expr-voice-2-m")
            voice_for_model = voice_mapping.get(voice, voice)

            logger.info(
                f"Generating speech: model={model_key}, voice={voice}, "
                f"speed={speed}, length={len(text)} chars"
            )

            # Generate audio using KittenTTS
            # The generate method returns numpy array
            audio = model_instance.generate(text=text, voice=voice_for_model)

            # Apply speed modification if needed
            if speed != 1.0:
                audio = self._apply_speed(audio, speed)

            # Convert to WAV bytes
            wav_bytes = self._numpy_to_wav(audio, sample_rate=24000)

            logger.info(f"Audio generated: {len(wav_bytes)} bytes")
            return wav_bytes

        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            import traceback

            logger.error(traceback.format_exc())
            return None

    def _apply_speed(self, audio: np.ndarray, speed: float) -> np.ndarray:
        """
        Apply speed modification to audio.

        Args:
            audio: Input audio array
            speed: Speed multiplier (>1 = faster, <1 = slower)

        Returns:
            Modified audio array
        """
        if speed == 1.0:
            return audio

        # Simple resampling for speed change
        # More sophisticated methods could be used (e.g., Phase Vocoder)
        indices = np.linspace(0, len(audio) - 1, int(len(audio) / speed))
        return np.interp(indices, np.arange(len(audio)), audio)

    def _numpy_to_wav(self, audio: np.ndarray, sample_rate: int = 24000) -> bytes:
        """
        Convert numpy array to WAV bytes.

        Args:
            audio: Audio samples as numpy array
            sample_rate: Audio sample rate

        Returns:
            WAV file bytes
        """
        # Ensure float32 format
        if audio.dtype != np.float32:
            audio = audio.astype(np.float32)

        # Normalize if needed
        max_val = np.max(np.abs(audio))
        if max_val > 1.0:
            audio = audio / max_val

        # Write to bytes buffer
        buffer = io.BytesIO()
        sf.write(buffer, audio, sample_rate, format="WAV", subtype="PCM_16")
        buffer.seek(0)

        return buffer.read()

    def estimate_duration(self, text: str, speed: float = 1.0) -> float:
        """
        Estimate audio duration based on character count.

        Args:
            text: Input text
            speed: Speed multiplier

        Returns:
            Estimated duration in seconds
        """
        # Rough estimate: ~15 chars per second at normal speed
        chars_per_second = 15 * speed
        return len(text) / chars_per_second


# Global service instance
tts_service = TTSService()
