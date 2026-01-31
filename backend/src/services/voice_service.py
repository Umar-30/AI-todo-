"""
Voice Service for STT (Speech-to-Text) and TTS (Text-to-Speech) operations.

Provides stateless voice processing using OpenAI Whisper and TTS APIs.
"""
import base64
import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

from openai import AsyncOpenAI

from ..config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionResult:
    """
    Result of speech-to-text operation.

    Attributes:
        text: Transcribed text (None on failure)
        confidence: Confidence score (0-1), if available
        error: Error message if transcription failed
    """
    text: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        """Check if transcription was successful."""
        return self.text is not None and self.error is None


class VoiceService:
    """
    Handles STT and TTS operations using OpenAI APIs.

    Stateless - each method is a pure function with API calls.
    Uses OpenRouter for API access (OpenAI-compatible).
    """

    def __init__(self):
        """Initialize VoiceService with OpenAI client."""
        settings = get_settings()

        # Use OpenAI API directly for audio (OpenRouter doesn't support audio APIs)
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

        # Voice settings from config
        # TTS voice options: alloy, echo, fable, onyx, nova, shimmer, coral
        self.default_voice = settings.tts_voice
        self.tts_model = settings.tts_model
        self.stt_model = settings.whisper_model

    async def transcribe(
        self,
        audio: bytes,
        content_type: str,
        filename: str = "audio.webm"
    ) -> TranscriptionResult:
        """
        Convert audio to text using OpenAI Whisper API.

        Args:
            audio: Raw audio bytes
            content_type: MIME type of audio (e.g., "audio/webm")
            filename: Filename for the audio (helps API detect format)

        Returns:
            TranscriptionResult with text or error
        """
        logger.info(f"Transcribing audio: {len(audio)} bytes, type={content_type}")

        try:
            # Create a file-like object from bytes
            audio_file = BytesIO(audio)
            audio_file.name = filename

            # Call Whisper API
            response = await self.client.audio.transcriptions.create(
                model=self.stt_model,
                file=audio_file,
                response_format="text",
            )

            # Response is the transcribed text directly
            transcript = response.strip() if isinstance(response, str) else str(response).strip()

            if not transcript:
                logger.warning("Transcription returned empty text")
                return TranscriptionResult(
                    error="No speech detected in audio"
                )

            logger.info(f"Transcription successful: '{transcript[:50]}...'")
            return TranscriptionResult(text=transcript)

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return TranscriptionResult(
                error=f"Transcription failed: {str(e)}"
            )

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> bytes:
        """
        Convert text to audio using OpenAI TTS API.

        Args:
            text: Text to convert to speech
            voice: Voice name (alloy, echo, fable, onyx, nova, shimmer)

        Returns:
            MP3 audio bytes

        Raises:
            Exception: If TTS fails
        """
        voice = voice or self.default_voice
        logger.info(f"Synthesizing speech: '{text[:50]}...' with voice={voice}")

        try:
            response = await self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=text,
                response_format="mp3",
            )

            # Read the audio content
            audio_bytes = response.content

            logger.info(f"TTS successful: {len(audio_bytes)} bytes generated")
            return audio_bytes

        except Exception as e:
            logger.error(f"TTS failed: {e}")
            raise

    def encode_audio_base64(self, audio_bytes: bytes) -> str:
        """
        Encode audio bytes to base64 string.

        Args:
            audio_bytes: Raw audio bytes

        Returns:
            Base64-encoded string
        """
        return base64.b64encode(audio_bytes).decode("utf-8")


# Factory function for creating VoiceService instances
def create_voice_service() -> VoiceService:
    """Create a new VoiceService instance."""
    return VoiceService()
