from gtts import gTTS
import io
import logging
import anyio

logger = logging.getLogger(__name__)

class TTSService:
    async def speak(self, text: str) -> bytes:
        """
        Converts text to speech using Google TTS (free, keyless) in Hindi/Hinglish.
        Runs the blocking gTTS operations in a worker thread.
        """
        if not text:
            return b""
            
        try:
            def generate_gtts():
                tts = gTTS(text=text, lang='hi')
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                return fp.getvalue()
                
            return await anyio.to_thread.run_sync(generate_gtts)
        except Exception as e:
            logger.error(f"gTTS speak failed: {e}")
            raise e

tts_service = TTSService()
