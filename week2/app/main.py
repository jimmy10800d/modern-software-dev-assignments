from __future__ import annotations  # 延後型別評估

from pathlib import Path  # 路徑處理
from typing import Any, Dict, Optional  # 型別註解

from fastapi import FastAPI, HTTPException  # FastAPI 與錯誤
from fastapi.responses import HTMLResponse  # HTML 回應
from fastapi.staticfiles import StaticFiles  # 靜態檔案服務

from .db import init_db  # 初始化資料庫
from .routers import action_items, notes  # 路由模組
from . import db  # 資料庫模組

init_db()  # 啟動時初始化資料庫

app = FastAPI(title="Action Item Extractor")  # 建立應用程式


@app.get("/", response_class=HTMLResponse)  # 首頁路由
def index() -> str:  # 回傳首頁 HTML
    html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"  # HTML 路徑
    return html_path.read_text(encoding="utf-8")  # 讀取並回傳內容


app.include_router(notes.router)  # 掛載筆記路由
app.include_router(action_items.router)  # 掛載行動項目路由


static_dir = Path(__file__).resolve().parents[1] / "frontend"  # 靜態檔案目錄
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")  # 掛載靜態路由