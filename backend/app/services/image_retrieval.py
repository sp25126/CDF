import urllib.parse
import uuid
import logging
import httpx
from bs4 import BeautifulSoup
from typing import List, Optional
from app.schemas.visual import VisualRef
from app.services.image_validator import verify_image_url

logger = logging.getLogger(__name__)

def strip_html(text: str) -> str:
    """Utility to strip HTML tags from string."""
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(strip=True)

async def retrieve_visuals(topic: str, class_level: Optional[str] = None) -> List[VisualRef]:
    """
    Retrieves and validates visuals for a given topic via Wikimedia Commons API.
    Returns 1-3 verified, loadable images or an empty list if none are reachable.
    """
    # Fetch from Wikimedia Commons API
    query = urllib.parse.quote(topic)
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch={query}&gsrlimit=5&prop=imageinfo&iiprop=url|extmetadata"
    
    headers = {
        "User-Agent": "ShikshaSahayak/1.0 (contact: contact@shikshasahayak.org)"
    }
    
    candidates = []
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                for page_id, page_data in pages.items():
                    title = page_data.get("title", "").replace("File:", "").split(".")[0]
                    image_info = page_data.get("imageinfo", [{}])[0]
                    image_url = image_info.get("url", "")
                    
                    # Try to get smaller thumbnail if it's an svg or large image to match earlier logic
                    # Or just use the original URL since we validate it.
                    
                    if not image_url:
                        continue
                        
                    extmetadata = image_info.get("extmetadata", {})
                    
                    description_html = extmetadata.get("ImageDescription", {}).get("value", "")
                    description = strip_html(description_html)
                    
                    if not description:
                        description = f"Image showing {topic}"
                        
                    artist_html = extmetadata.get("Artist", {}).get("value", "")
                    source = strip_html(artist_html) or "Wikimedia Commons"

                    candidates.append(
                        VisualRef(
                            type="image",
                            url=image_url,
                            description=description[:200],  # Short description
                            title=title,
                            alt_text=description[:100],
                            source=source,
                            reason=f"Found relevant image for {topic}",
                            visual_id=str(uuid.uuid4())
                        )
                    )
    except Exception as e:
        logger.error(f"[ImageRetrieval] Error fetching from Wikimedia: {e}")

    # Validate candidates and return up to 3
    verified_visuals = []
    for vis in candidates:
        if len(verified_visuals) >= 3:
            break
        if await verify_image_url(vis.url):
            verified_visuals.append(vis)
        else:
            logger.warning(f"[ImageRetrieval] URL failed verification: {vis.url}")
            
    return verified_visuals
