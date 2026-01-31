from pathlib import Path  # 路徑處理

from fastapi import FastAPI  # FastAPI 應用
from fastapi.responses import FileResponse  # 檔案回應
from fastapi.staticfiles import StaticFiles  # 靜態檔案服務

from .db import apply_seed_if_needed, engine  # 資料庫初始化
from .models import Base  # ORM Base
from .routers import action_items as action_items_router  # 行動項目路由
from .routers import notes as notes_router  # 筆記路由

app = FastAPI(title="Modern Software Dev Starter (Week 6)", version="0.1.0")  # 建立應用

_WEEK_DIR = Path(__file__).resolve().parents[2]  # week7 目錄
_DATA_DIR = _WEEK_DIR / "data"  # 資料夾
_FRONTEND_DIR = _WEEK_DIR / "frontend"  # 前端目錄

# Ensure data dir exists (relative to week folder, not current working directory)
_DATA_DIR.mkdir(parents=True, exist_ok=True)  # 建立資料夾

# Mount static frontend (avoid import-time crash if cwd is different)
if _FRONTEND_DIR.exists():  # 若前端存在
    app.mount("/static", StaticFiles(directory=str(_FRONTEND_DIR)), name="static")  # 掛載靜態路由


# Compatibility with FastAPI lifespan events; keep on_event for simplicity here
@app.on_event("startup")  # 啟動事件
def startup_event() -> None:  # 啟動時初始化
    Base.metadata.create_all(bind=engine)  # 建立資料表
    apply_seed_if_needed()  # 套用 seed


@app.get("/")  # 首頁路由
async def root() -> FileResponse:  # 回傳前端首頁
    return FileResponse(str(_FRONTEND_DIR / "index.html"))  # 回傳檔案


# Routers
app.include_router(notes_router.router)  # 掛載筆記路由
app.include_router(action_items_router.router)  # 掛載行動項目路由


