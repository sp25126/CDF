import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import sessions, sources
from app.routers import command_router
from app.core.config import get_settings

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}

# Include Routers
app.include_router(command_router.router, prefix="/api/v1/command", tags=["commands"])
app.include_router(sessions.router, prefix="/api/v1/session", tags=["sessions"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["sources"])

# Support alternative direct prefixes for testing compatibility
app.include_router(command_router.router, prefix="/command", tags=["commands"])
app.include_router(sessions.router, prefix="/session", tags=["sessions"])
app.include_router(sources.router, prefix="/sources", tags=["sources"])

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Shiksha Sahayak Backend...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
