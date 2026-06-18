"""
Image Retrieval — topic-locked Wikimedia Commons search with strict relevance gating.

Pipeline:
  1. Build topic-locked search query (not generic science keywords)
  2. Search Wikimedia Commons API
  3. Validate each URL is a real, loadable image
  4. Run strict semantic relevance filter
  5. Return only images that pass ALL checks
  6. Return empty list if nothing passes — NEVER a "close enough" fallback
"""
import urllib.parse
import uuid
import logging
import httpx
from bs4 import BeautifulSoup
from typing import List, Optional

from app.schemas.visual import VisualRef
from app.services.image_validator import verify_image_url
from app.services.image_relevance_filter import is_image_relevant, find_topic_profile

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "ShikshaSahayak/1.0 (contact: contact@shikshasahayak.org)"
}

# Max candidates to fetch before filtering (keep small for speed)
FETCH_LIMIT = 12

# Allowed image extensions — must be an actual raster image
ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"}


def _is_image_url(url: str) -> bool:
    """Return True only if the URL points to a raster or vector image file."""
    path = url.lower().split("?")[0]  # strip query params
    return any(path.endswith(ext) for ext in ALLOWED_IMAGE_EXTS)


def strip_html(text: str) -> str:
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(strip=True)


def _build_search_query(topic: str) -> str:
    """
    Build a topic-locked Wikimedia search query.
    Avoids generic "science diagram" searches that pull off-topic results.
    """
    profile = find_topic_profile(topic)

    if profile and profile.get("required"):
        # Anchor the search to the 3 most specific required keywords + the topic itself
        anchors = profile["required"][:3]
        anchor_str = " ".join(anchors)
        return f"{topic} {anchor_str} diagram"
    else:
        # Simple title search — include "diagram" to prefer educational visuals
        return f"{topic} educational diagram"


async def retrieve_visuals(
    topic: str, class_level: Optional[str] = None
) -> List[VisualRef]:
    """
    Fetch, validate, and relevance-filter images for a topic.
    Returns 0–3 verified, topic-locked images. Empty list if none qualify.
    """
    search_query = _build_search_query(topic)
    encoded_q = urllib.parse.quote(search_query)

    url = (
        f"https://commons.wikimedia.org/w/api.php"
        f"?action=query&format=json&generator=search"
        f"&gsrnamespace=6&gsrsearch={encoded_q}&gsrlimit={FETCH_LIMIT}"
        f"&gsrfiletype=bitmap"  # bitmap = jpg/png/gif — excludes PDFs, videos
        f"&prop=imageinfo&iiprop=url|extmetadata"
    )

    raw_candidates = []
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(url, headers=HEADERS)
            if resp.status_code != 200:
                logger.warning(f"[ImageRetrieval] Wikimedia API returned {resp.status_code}")
                return []

            data = resp.json()
            pages = data.get("query", {}).get("pages", {})

            for _page_id, page_data in pages.items():
                raw_title = page_data.get("title", "").replace("File:", "")
                title = raw_title.rsplit(".", 1)[0]  # strip extension

                image_info = page_data.get("imageinfo", [{}])[0]
                image_url = image_info.get("url", "")
                if not image_url:
                    continue

                # Early skip: reject non-image file types (PDFs, videos, etc.)
                if not _is_image_url(image_url):
                    logger.debug(f"[ImageRetrieval] Skipping non-image URL: {image_url[-50:]}")
                    continue

                extmetadata = image_info.get("extmetadata", {})
                description_html = extmetadata.get("ImageDescription", {}).get("value", "")
                description = strip_html(description_html) or f"Image related to {topic}"

                artist_html = extmetadata.get("Artist", {}).get("value", "")
                source = strip_html(artist_html) or "Wikimedia Commons"

                raw_candidates.append({
                    "title": title,
                    "url": image_url,
                    "description": description[:300],
                    "alt_text": description[:100],
                    "source": source,
                })

    except Exception as e:
        logger.error(f"[ImageRetrieval] Wikimedia fetch error: {e}")
        return []

    if not raw_candidates:
        logger.info(f"[ImageRetrieval] No candidates returned from Wikimedia for '{topic}'")
        return []

    # ── Step 1: URL validation + relevance filter ──────────────────────────────
    verified = []
    for cand in raw_candidates:
        if len(verified) >= 3:
            break

        # A) URL must be loadable
        if not await verify_image_url(cand["url"]):
            logger.warning(f"[ImageRetrieval] URL failed validation: {cand['url']}")
            continue

        # B) Relevance filter — strict semantic check
        passes, score, reason = is_image_relevant(
            topic=topic,
            image_title=cand["title"],
            image_description=cand["description"],
            image_alt_text=cand["alt_text"],
            image_source=cand["source"],
        )

        if not passes:
            logger.info(
                f"[ImageRetrieval] Relevance REJECT: '{cand['title'][:60]}' "
                f"score={score:.2f} reason={reason}"
            )
            continue

        verified.append(
            VisualRef(
                type="image",
                url=cand["url"],
                description=cand["description"],
                title=cand["title"],
                alt_text=cand["alt_text"],
                source=cand["source"],
                reason=f"Relevance score {score:.2f} for topic '{topic}'",
                visual_id=str(uuid.uuid4()),
            )
        )

    logger.info(
        f"[ImageRetrieval] topic='{topic}' → "
        f"{len(raw_candidates)} fetched, {len(verified)} passed all filters"
    )
    return verified
