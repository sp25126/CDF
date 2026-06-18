"""
YouTube URL Validator — strict pipeline to ensure only real, playable YouTube links.

Validation rules:
  1. Domain must be youtube.com or youtu.be
  2. Video ID must be exactly 11 alphanumeric characters
  3. Must not be a channel, playlist, or short redirect
  4. Constructs canonical watch + embed URLs
  5. No LLM involvement in URL selection
"""
import re
import logging
from typing import Optional
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

# YouTube video ID pattern — always exactly 11 chars
YT_ID_RE = re.compile(r"^[A-Za-z0-9_\-]{11}$")

# Trusted YouTube domains
YT_DOMAINS = {"youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"}

# URL patterns that indicate a channel or playlist (not a single video)
YT_NON_VIDEO_PATHS = re.compile(
    r"^/(channel/|c/|user/|playlist\?|@|shorts/)",
    re.IGNORECASE,
)


def extract_youtube_id(url_or_id: str) -> Optional[str]:
    """
    Extract the YouTube video ID from a full URL or a raw ID string.
    Returns None if invalid or not a single video.
    """
    if not url_or_id:
        return None

    s = url_or_id.strip()

    # Case 1: Raw 11-char ID
    if YT_ID_RE.match(s):
        return s

    # Case 2: Full URL
    try:
        parsed = urlparse(s if "://" in s else f"https://{s}")
    except Exception:
        return None

    domain = parsed.netloc.lower().lstrip("www.")
    if domain not in YT_DOMAINS and f"www.{domain}" not in YT_DOMAINS:
        logger.debug(f"[YTValidate] Non-YouTube domain: {domain}")
        return None

    # Reject channels / playlists
    if YT_NON_VIDEO_PATHS.match(parsed.path):
        logger.debug(f"[YTValidate] Non-video path rejected: {parsed.path}")
        return None

    # youtu.be/<ID>
    if "youtu.be" in parsed.netloc:
        vid_id = parsed.path.lstrip("/").split("?")[0].split("/")[0]
        if YT_ID_RE.match(vid_id):
            return vid_id
        return None

    # youtube.com/watch?v=<ID>
    qs = parse_qs(parsed.query)
    if "v" in qs:
        vid_id = qs["v"][0]
        if YT_ID_RE.match(vid_id):
            return vid_id

    # youtube.com/embed/<ID>
    embed_match = re.search(r"/embed/([A-Za-z0-9_\-]{11})", parsed.path)
    if embed_match:
        return embed_match.group(1)

    # youtube.com/v/<ID>
    v_match = re.search(r"/v/([A-Za-z0-9_\-]{11})", parsed.path)
    if v_match:
        return v_match.group(1)

    return None


def build_video_urls(video_id: str) -> dict:
    """Build canonical watch and embed URLs from a validated ID."""
    return {
        "watch_url": f"https://www.youtube.com/watch?v={video_id}",
        "embed_url": f"https://www.youtube.com/embed/{video_id}",
        "youtube_id": video_id,
    }


def validate_youtube_entry(url_or_id: str) -> Optional[dict]:
    """
    Full validation of a YouTube URL or ID.
    Returns {youtube_id, watch_url, embed_url} if valid, else None.
    """
    vid_id = extract_youtube_id(url_or_id)
    if not vid_id:
        logger.warning(f"[YTValidate] Invalid or non-video YouTube input: '{url_or_id}'")
        return None

    result = build_video_urls(vid_id)
    logger.debug(f"[YTValidate] Valid: {result['watch_url']}")
    return result
