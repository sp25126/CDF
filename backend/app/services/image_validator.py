import logging
import httpx

logger = logging.getLogger(__name__)

async def verify_image_url(url: str) -> bool:
    """
    Perform a fast asynchronous HEAD or GET request to verify a URL is loadable 
    and points to a valid image format.
    """
    if not url or not url.startswith("http"):
        return False

    headers = {
        "User-Agent": "ShikshaSahayak/1.0 (contact: contact@shikshasahayak.org)"
    }
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.head(url, headers=headers)
            
            # If HEAD fails or is blocked, fallback to GET (with streaming to avoid downloading large files)
            if resp.status_code != 200:
                async with client.stream("GET", url, headers=headers) as get_resp:
                    if get_resp.status_code != 200:
                        return False
                    content_type = get_resp.headers.get("Content-Type", "")
                    return content_type.startswith("image/")
            
            # HEAD request was successful, verify content type
            content_type = resp.headers.get("Content-Type", "")
            if content_type.startswith("image/"):
                return True
            else:
                # Sometimes HEAD returns wrong headers, fallback to GET to be safe
                async with client.stream("GET", url, headers=headers) as get_resp:
                    content_type = get_resp.headers.get("Content-Type", "")
                    return get_resp.status_code == 200 and content_type.startswith("image/")

    except Exception as e:
        logger.warning(f"[ImageValidator] URL verification failed for {url}: {e}")
        return False
