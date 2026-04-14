from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import routes_analyze, routes_feedback, routes_metadata, routes_pathway
from app.config import get_settings
from app.db.session import init_db

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
    except Exception as e:
        log.warning("Database init failed (%s). Check DATABASE_URL or delete stale SQLite file.", e)
    yield


app = FastAPI(title=get_settings().app_name, lifespan=lifespan)
_settings = get_settings()
_cors_regex = (_settings.cors_origin_regex or "").strip()
if _cors_regex:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=_cors_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    _origins = [o.strip() for o in _settings.cors_origins.split(",") if o.strip()]
    _open = not _origins or (len(_origins) == 1 and _origins[0] == "*")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if _open else _origins,
        allow_credentials=not _open,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(routes_analyze.router)
app.include_router(routes_pathway.router)
app.include_router(routes_feedback.router)
app.include_router(routes_metadata.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Serve the built React frontend from `frontend/dist` (so UI + API share one server).
_repo_root = Path(__file__).resolve().parents[2]
_frontend_dist = _repo_root / "frontend" / "dist"
if _frontend_dist.exists():
    # Vite build references assets like `/assets/index-*.js`.
    _frontend_assets = _frontend_dist / "assets"
    if _frontend_assets.exists():
        app.mount("/assets", StaticFiles(directory=str(_frontend_assets)), name="frontend-assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str) -> FileResponse:
        # For SPA routing and non-API routes, return the React entrypoint.
        # Note: `/v1/*` and `/health` are declared above and will match first.
        _ = full_path
        return FileResponse(str(_frontend_dist / "index.html"))
