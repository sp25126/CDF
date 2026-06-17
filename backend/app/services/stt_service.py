import io
import httpx
import logging
import anyio
import speech_recognition as sr
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class STTService:
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.url = "https://api.openai.com/v1/audio/transcriptions"
        self.recognizer = sr.Recognizer()

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        """
        Transcribes audio bytes. Tries OpenAI Whisper first if a standard key is available.
        Otherwise, falls back to keyless Google Speech Recognition with parallel English/Hindi auto-detection.
        """
        # 1. Try standard OpenAI Whisper if key looks valid
        if self.api_key and "sk-or-" not in self.api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }
                files = {
                    "file": (filename, audio_bytes, "audio/wav")
                }
                data = {
                    "model": "whisper-1"
                }
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(self.url, headers=headers, files=files, data=data)
                    response.raise_for_status()
                    result = response.json()
                    transcript = result.get("text", "").strip()
                    if transcript:
                        logger.info(f"OpenAI Whisper transcribed: '{transcript}'")
                        return transcript
            except Exception as e:
                logger.error(f"OpenAI Whisper STT failed: {e}. Falling back to keyless STT.")

        # 2. Keyless Google Speech API fallback with English/Hindi auto-detection
        logger.info("Using keyless Google STT with parallel English/Hindi auto-detection...")
        return await self._transcribe_keyless_multilingual(audio_bytes)

    async def _transcribe_keyless_multilingual(self, audio_bytes: bytes) -> str:
        audio_file = io.BytesIO(audio_bytes)
        try:
            with sr.AudioFile(audio_file) as source:
                audio_data = self.recognizer.record(source)
        except Exception as e:
            logger.error(f"Failed to parse audio file for keyless STT: {e}")
            return ""

        def transcribe_sync(audio, lang: str) -> str:
            try:
                return self.recognizer.recognize_google(audio, language=lang)
            except Exception:
                return ""

        # Run English and Hindi transcription concurrently in worker threads
        text_en = ""
        text_hi = ""

        async def fetch_en():
            nonlocal text_en
            text_en = await anyio.to_thread.run_sync(transcribe_sync, audio_data, "en-US")

        async def fetch_hi():
            nonlocal text_hi
            text_hi = await anyio.to_thread.run_sync(transcribe_sync, audio_data, "hi-IN")

        try:
            async with anyio.create_task_group() as tg:
                tg.start_soon(fetch_en)
                tg.start_soon(fetch_hi)
        except Exception as e:
            logger.error(f"Parallel keyless STT tasks failed: {e}")

        text_en = text_en.strip()
        text_hi = text_hi.strip()

        logger.info(f"Keyless STT raw results - English: '{text_en}', Hindi: '{text_hi}'")

        if not text_en and not text_hi:
            return ""

        if not text_en:
            return text_hi

        if not text_hi:
            return text_en

        # Heuristic: Check if the Hindi transcript contains Devanagari characters (Unicode range \u0900-\u097F)
        has_devanagari = any('\u0900' <= char <= '\u097f' for char in text_hi)

        if has_devanagari:
            # The speaker spoke in Hindi/Hinglish and the hi-IN engine outputted Devanagari
            logger.info("Auto-detected language: Hindi")
            return text_hi
        else:
            # No Devanagari characters, the speaker spoke English (or hi-IN returned Latin text)
            logger.info("Auto-detected language: English")
            return text_en

stt_service = STTService()
