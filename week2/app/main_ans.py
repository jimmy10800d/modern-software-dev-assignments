"""
Week2 TODO 3 & 4 解答：重構主應用程式
main_ans.py - 改進生命週期管理、錯誤處理、新增 LLM 端點
"""
from __future__ import annotations  # 延後型別評估

import logging  # 日誌模組
from pathlib import Path  # 路徑處理
from typing import Any, Dict, Optional  # 型別註解
from contextlib import asynccontextmanager  # 非同步上下文管理器

from fastapi import FastAPI, HTTPException, Request  # FastAPI 核心
from fastapi.responses import HTMLResponse, JSONResponse  # 回應類型
from fastapi.staticfiles import StaticFiles  # 靜態檔案服務
from fastapi.middleware.cors import CORSMiddleware  # CORS 中介軟體
from pydantic import ValidationError  # Pydantic 驗證錯誤

from .db import init_db  # 初始化資料庫
from .routers import action_items, notes  # 路由模組
from .schemas_ans import HealthResponse, StatsResponse, ErrorResponse  # Schema 模組
from . import db  # 資料庫操作

# ============================================================
# 設定日誌
# ============================================================

logging.basicConfig(
    level=logging.INFO,  # 日誌等級
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # 格式
)
logger = logging.getLogger(__name__)  # 建立日誌器


# ============================================================
# 應用程式生命週期管理
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理
    
    在啟動時初始化資料庫，在關閉時執行清理。
    """
    # 啟動事件
    logger.info("Application starting up...")
    try:
        init_db()  # 初始化資料庫
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield  # 應用程式運行中
    
    # 關閉事件
    logger.info("Application shutting down...")


# ============================================================
# 建立 FastAPI 應用程式
# ============================================================

app = FastAPI(
    title="Action Item Extractor",  # 應用程式標題
    description="Extract actionable items from free-form notes using heuristics or LLM",  # 描述
    version="2.0.0",  # 版本
    lifespan=lifespan,  # 生命週期管理
    docs_url="/docs",  # Swagger UI 路徑
    redoc_url="/redoc",  # ReDoc 路徑
)


# ============================================================
# 中介軟體配置
# ============================================================

# CORS 設定（允許前端跨域請求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源（生產環境應限制）
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有標頭
)


# ============================================================
# 全域錯誤處理
# ============================================================

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """處理 Pydantic 驗證錯誤"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """處理 HTTP 例外"""
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """處理未預期的錯誤"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================
# 路由配置
# ============================================================

# 首頁路由 - 回傳前端 HTML
@app.get("/", response_class=HTMLResponse, tags=["frontend"])
def index() -> str:
    """首頁 - 回傳前端 HTML 頁面
    
    讀取並回傳 frontend/index.html 的內容。
    """
    # 嘗試讀取新版前端（index_ans.html），若不存在則讀取原版
    frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
    
    # 優先使用答案版本
    html_path = frontend_dir / "index_ans.html"
    if not html_path.exists():
        html_path = frontend_dir / "index.html"
    
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    
    return html_path.read_text(encoding="utf-8")


# 健康檢查端點
@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    """健康檢查端點
    
    回傳服務狀態與版本資訊。
    """
    return HealthResponse(status="ok", version="2.0.0")


# 統計資訊端點
@app.get("/stats", response_model=StatsResponse, tags=["health"])
def get_stats() -> StatsResponse:
    """取得統計資訊
    
    回傳筆記與行動項目的統計數據。
    """
    try:
        # 使用重構後的 db 模組（若存在），否則使用原版
        try:
            from .db_ans import get_stats as db_get_stats
            stats = db_get_stats()
        except ImportError:
            # 使用原版 db 模組計算統計
            notes_list = db.list_notes()
            items_list = db.list_action_items()
            done_count = sum(1 for item in items_list if item["done"])
            stats = {
                "notes_count": len(notes_list),
                "action_items_count": len(items_list),
                "completed_items_count": done_count,
                "pending_items_count": len(items_list) - done_count
            }
        
        return StatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


# ============================================================
# 掛載路由
# ============================================================

# 掛載筆記路由
app.include_router(notes.router)

# 掛載行動項目路由
app.include_router(action_items.router)


# ============================================================
# 靜態檔案服務
# ============================================================

# 掛載靜態檔案目錄
static_dir = Path(__file__).resolve().parents[1] / "frontend"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ============================================================
# API 文件說明
# ============================================================

@app.get("/api/info", tags=["info"])
def api_info() -> Dict[str, Any]:
    """取得 API 資訊
    
    回傳可用的端點列表與說明。
    """
    return {
        "title": "Action Item Extractor API",
        "version": "2.0.0",
        "endpoints": {
            "notes": {
                "POST /notes": "Create a new note",
                "GET /notes": "List all notes",
                "GET /notes/{id}": "Get a specific note"
            },
            "action_items": {
                "POST /action-items/extract": "Extract action items (heuristic)",
                "POST /action-items/extract-llm": "Extract action items (LLM)",
                "GET /action-items": "List all action items",
                "POST /action-items/{id}/done": "Mark item as done"
            },
            "health": {
                "GET /health": "Health check",
                "GET /stats": "Get statistics"
            }
        }
    }
