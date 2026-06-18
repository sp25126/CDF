"""
TTS Service — Google TTS with markdown cleaning before speech synthesis.

The AI often returns markdown (*bold*, **strong**, # headers, bullet lists).
These must be stripped before passing to gTTS, otherwise the AI literally
says "asterisk asterisk" or reads punctuation aloud.
"""
from gtts import gTTS
import io
import re
import logging
import anyio

logger = logging.getLogger(__name__)


def clean_for_speech(text: str) -> str:
    """
    Strip markdown formatting and clean up text for natural speech synthesis.
    
    Removes:
    - **bold** and *italic* markers
    - # heading markers
    - Bullet points (* -, •)
    - Backtick code spans
    - Excessive punctuation that causes unnatural pauses
    - HTML tags
    - Trailing/leading whitespace and duplicate spaces
    """
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove markdown headings (# ## ###)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Remove bold/italic markers (**text** *text* __text__ _text_)
    text = re.sub(r"\*{1,3}([^*\n]+)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,2}([^_\n]+)_{1,2}", r"\1", text)

    # Remove inline code backticks
    text = re.sub(r"`[^`]+`", lambda m: m.group(0).strip("`"), text)

    # Convert bullet list markers to natural pause (comma or period)
    # "* item" or "- item" or "• item" at line start
    text = re.sub(r"^\s*[\*\-•]\s+", "", text, flags=re.MULTILINE)

    # Remove numbered list markers like "1. " "2) "
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.MULTILINE)

    # Remove any remaining lone asterisks or underscores
    text = re.sub(r"(?<!\w)\*+(?!\w)", "", text)
    text = re.sub(r"(?<!\w)_+(?!\w)", "", text)

    # Normalize multiple newlines/spaces to single space
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)

    return text.strip()


class TTSService:
    async def speak(self, text: str) -> bytes:
        """
        Converts text to speech using Google TTS in Hindi/Hinglish.
        Strips markdown formatting before synthesis so the AI doesn't say
        "asterisk asterisk" or read bullet point symbols aloud.
        """
        if not text:
            return b""

        # Clean markdown before TTS
        clean_text = clean_for_speech(text)
        if not clean_text:
            return b""

        logger.debug(f"[TTS] Speaking ({len(clean_text)} chars): {clean_text[:80]}...")

        try:
            def generate_gtts():
                tts = gTTS(text=clean_text, lang="hi")
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                return fp.getvalue()

            return await anyio.to_thread.run_sync(generate_gtts)
        except Exception as e:
            logger.error(f"[TTS] gTTS speak failed: {e}")
            raise e


tts_service = TTSService()
