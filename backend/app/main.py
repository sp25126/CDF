import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.routes import sessions, sources
from .api.routes import commands as api_commands
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
    debug=settings.DEBUG,
    description=(
        "Shiksha Sahayak — AI classroom assistant backend. "
        "All /api/* routes return a consistent GlobalResponse envelope."
    ),
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Origins are set via ALLOWED_ORIGINS env var (comma-separated).
# In development the Next.js proxy forwards /api/* so CORS is not needed
# for same-origin calls; this config covers direct curl / Postman / other origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Session-Id", "Accept"],
)

# ─── Global error handler — never expose raw stack traces ─────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "data": None,
            "error": {
                "code": "SERVER_ERROR",
                "message": "The assistant ran into an unexpected problem. Please try again."
            }
        }
    )

# ─── Health ───────────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "ok", "version": settings.VERSION}

# ─── Primary /api/* routes (versioned, frontend-facing) ───────────────────────
# POST /api/command          — unified command (Prompt 1)
app.include_router(api_commands.router, prefix="/api/command", tags=["commands"])

# GET/POST /api/session/{id} — live session CRUD (Prompt 1)
app.include_router(sessions.router, prefix="/api/session", tags=["sessions"])

# Sources management
app.include_router(sources.router, prefix="/api/sources", tags=["sources"])

# Voice / hands-free
app.include_router(voice_router.router, prefix="/api/voice", tags=["voice"])

# ─── Legacy compatibility routes (keep old tests + direct calls working) ───────
app.include_router(command_router.router, prefix="/command", tags=["commands-legacy"])
app.include_router(command_router.router, prefix="/api/v1/command", tags=["commands-legacy"])
app.include_router(sessions.router, prefix="/session", tags=["sessions-legacy"])
app.include_router(sessions.router, prefix="/api/v1/session", tags=["sessions-legacy"])
app.include_router(sources.router, prefix="/sources", tags=["sources-legacy"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["sources-legacy"])
app.include_router(voice_router.router, prefix="/voice", tags=["voice-legacy"])

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Shiksha Sahayak Backend…")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
