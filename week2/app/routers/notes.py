from __future__ import annotations  # 延後型別評估

from typing import Any, Dict, List  # 型別註解

from fastapi import APIRouter, HTTPException  # FastAPI 路由與錯誤

from .. import db  # 資料庫操作
from ..schemas import (  # TODO 3: 使用 Pydantic schemas
    NoteCreate,
    NoteResponse,
    NoteListResponse,
)


router = APIRouter(prefix="/notes", tags=["notes"])  # 設定路由前綴與標籤


# ============================================================================
# TODO 4: 新增列出所有筆記的端點
# ============================================================================

@router.get("", response_model=NoteListResponse)  # 列出所有筆記 API
def list_notes() -> NoteListResponse:
    """
    列出所有筆記。
    
    回傳所有儲存的筆記，按建立時間倒序排列。
    """
    rows = db.list_notes()  # 查詢所有筆記
    notes = [
        NoteResponse(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"],
        )
        for row in rows
    ]
    return NoteListResponse(notes=notes, total=len(notes))


@router.post("", response_model=NoteResponse)  # 建立新增筆記 API
def create_note(payload: NoteCreate) -> NoteResponse:  # 使用 Pydantic 模型驗證請求
    """
    建立新筆記。
    """
    content = payload.content.strip()  # 取得內容
    if not content:  # 若內容為空
        raise HTTPException(status_code=400, detail="content is required")  # 回傳錯誤
    note_id = db.insert_note(content)  # 新增筆記
    note = db.get_note(note_id)  # 取得新增的筆記
    return NoteResponse(  # 回傳筆記資訊
        id=note["id"],
        content=note["content"],
        created_at=note["created_at"],
    )


@router.get("/{note_id}", response_model=NoteResponse)  # 取得單筆筆記 API
def get_single_note(note_id: int) -> NoteResponse:  # 取得筆記
    """
    取得單一筆記。
    """
    row = db.get_note(note_id)  # 查詢資料
    if row is None:  # 若不存在
        raise HTTPException(status_code=404, detail="note not found")  # 回傳錯誤
    return NoteResponse(
        id=row["id"],
        content=row["content"],
        created_at=row["created_at"],
    )


