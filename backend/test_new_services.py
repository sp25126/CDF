import asyncio
import sys
import os

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.services.image_retrieval import retrieve_visuals
from app.services.video_search import search_videos

async def main():
    print("Testing Image Retrieval...")
    visuals = await retrieve_visuals("photosynthesis")
    for v in visuals:
        print(f"- {v.title}: {v.url} ({v.source})")

    print("\nTesting Video Search...")
    videos = await search_videos("photosynthesis", "how does photosynthesis work?")
    if videos:
        print(f"Primary: {videos['primary']['video'].title}")
        for alt in videos.get('alternatives', []):
            print(f"Alt: {alt['video'].title}")
    else:
        print("No videos found.")

if __name__ == "__main__":
    asyncio.run(main())
