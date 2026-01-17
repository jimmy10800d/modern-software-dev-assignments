from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import apply_seed_if_needed, engine
from .models import Base
from .routers import action_items as action_items_router
from .routers import notes as notes_router

app = FastAPI(title="Modern Software Dev Starter (Week 5)")

_WEEK_DIR = Path(__file__).resolve().parents[2]
_DATA_DIR = _WEEK_DIR / "data"
_FRONTEND_DIR = _WEEK_DIR / "frontend"

# Ensure data dir exists (relative to week folder, not current working directory)
_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Mount static frontend (avoid import-time crash if cwd is different)
if _FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_FRONTEND_DIR)), name="static")


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    apply_seed_if_needed()


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(str(_FRONTEND_DIR / "index.html"))


# Routers
app.include_router(notes_router.router)
app.include_router(action_items_router.router)
