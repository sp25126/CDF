import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import sessions, sources
from .routers import command_router, voice_router
from .core.config import get_settings

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
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}

# Include Routers
app.include_router(command_router.router, prefix="/api/command", tags=["commands"])
app.include_router(command_router.router, prefix="/api/v1/command", tags=["commands"])
app.include_router(sessions.router, prefix="/api/v1/session", tags=["sessions"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["sources"])

# Include Voice router
app.include_router(voice_router.router, prefix="/api/voice", tags=["voice"])
app.include_router(voice_router.router, prefix="/voice", tags=["voice"])

# Support alternative direct prefixes for testing compatibility
app.include_router(command_router.router, prefix="/command", tags=["commands"])
app.include_router(sessions.router, prefix="/session", tags=["sessions"])
app.include_router(sources.router, prefix="/sources", tags=["sources"])
app.include_router(sources.router, prefix="/api/sources", tags=["sources"])

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Shiksha Sahayak Backend...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
