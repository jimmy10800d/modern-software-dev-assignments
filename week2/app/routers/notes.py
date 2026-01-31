from __future__ import annotations  # 延後型別評估

from typing import Any, Dict, List  # 型別註解

from fastapi import APIRouter, HTTPException  # FastAPI 路由與錯誤

from .. import db  # 資料庫操作


router = APIRouter(prefix="/notes", tags=["notes"])  # 設定路由前綴與標籤


@router.post("")  # 建立新增筆記 API
def create_note(payload: Dict[str, Any]) -> Dict[str, Any]:  # 建立筆記
    content = str(payload.get("content", "")).strip()  # 取得內容
    if not content:  # 若內容為空
        raise HTTPException(status_code=400, detail="content is required")  # 回傳錯誤
    note_id = db.insert_note(content)  # 新增筆記
    note = db.get_note(note_id)  # 取得新增的筆記
    return {  # 回傳筆記資訊
        "id": note["id"],
        "content": note["content"],
        "created_at": note["created_at"],
    }


@router.get("/{note_id}")  # 取得單筆筆記 API
def get_single_note(note_id: int) -> Dict[str, Any]:  # 取得筆記
    row = db.get_note(note_id)  # 查詢資料
    if row is None:  # 若不存在
        raise HTTPException(status_code=404, detail="note not found")  # 回傳錯誤
    return {"id": row["id"], "content": row["content"], "created_at": row["created_at"]}  # 回傳資料


