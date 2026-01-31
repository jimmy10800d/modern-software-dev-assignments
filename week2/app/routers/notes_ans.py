"""
Week2 TODO 3 & 4 解答：重構筆記路由
notes_ans.py - 使用 Pydantic schemas、新增列出所有筆記端點
"""
from __future__ import annotations  # 延後型別評估

from typing import Any, Dict, List  # 型別註解
import logging  # 日誌模組

from fastapi import APIRouter, HTTPException, Query  # FastAPI 路由與工具

from .. import db  # 資料庫操作
from ..schemas_ans import (  # Schema 模組
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    NoteListResponse,
    ErrorResponse
)

# ============================================================
# 設定
# ============================================================

logger = logging.getLogger(__name__)  # 建立日誌器

router = APIRouter(
    prefix="/notes",  # 路由前綴
    tags=["notes"],  # API 文件標籤
    responses={
        404: {"model": ErrorResponse, "description": "Note not found"},
        400: {"model": ErrorResponse, "description": "Bad request"}
    }
)


# ============================================================
# API 端點
# ============================================================

@router.post(
    "",
    response_model=NoteResponse,
    status_code=201,
    summary="建立新筆記",
    description="建立一個新的筆記並儲存到資料庫"
)
def create_note(payload: NoteCreate) -> NoteResponse:
    """建立新筆記
    
    Args:
        payload: 包含 content 的請求資料
        
    Returns:
        NoteResponse: 新建立的筆記資料
        
    Raises:
        HTTPException: 當內容為空或建立失敗時
    """
    try:
        content = payload.content.strip()  # 取得並清理內容
        
        if not content:  # 若內容為空
            raise HTTPException(status_code=400, detail="Content is required")
        
        note_id = db.insert_note(content)  # 新增筆記
        note = db.get_note(note_id)  # 取得新增的筆記
        
        if note is None:
            raise HTTPException(status_code=500, detail="Failed to create note")
        
        logger.info(f"Note created: id={note_id}")
        
        return NoteResponse(
            id=note["id"],
            content=note["content"],
            created_at=note["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        raise HTTPException(status_code=500, detail="Failed to create note")


@router.get(
    "",
    response_model=NoteListResponse,
    summary="列出所有筆記",
    description="取得所有已儲存的筆記列表"
)
def list_all_notes(
    limit: int = Query(100, ge=1, le=1000, description="回傳筆數上限"),
    offset: int = Query(0, ge=0, description="跳過筆數")
) -> NoteListResponse:
    """列出所有筆記（TODO 4 新增端點）
    
    Args:
        limit: 最大回傳數量
        offset: 跳過的筆數（用於分頁）
        
    Returns:
        NoteListResponse: 筆記列表與總數
    """
    try:
        rows = db.list_notes()  # 查詢所有筆記
        
        # 應用 offset 和 limit
        total = len(rows)
        paginated = rows[offset:offset + limit]
        
        notes = [
            NoteResponse(
                id=row["id"],
                content=row["content"],
                created_at=row["created_at"]
            )
            for row in paginated
        ]
        
        logger.info(f"Listed {len(notes)} notes (total: {total})")
        
        return NoteListResponse(notes=notes, total=total)
        
    except Exception as e:
        logger.error(f"Error listing notes: {e}")
        raise HTTPException(status_code=500, detail="Failed to list notes")


@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    summary="取得單一筆記",
    description="根據 ID 取得特定筆記"
)
def get_single_note(note_id: int) -> NoteResponse:
    """取得單一筆記
    
    Args:
        note_id: 筆記 ID
        
    Returns:
        NoteResponse: 筆記資料
        
    Raises:
        HTTPException: 當筆記不存在時
    """
    try:
        row = db.get_note(note_id)  # 查詢資料
        
        if row is None:  # 若不存在
            logger.warning(f"Note not found: id={note_id}")
            raise HTTPException(status_code=404, detail="Note not found")
        
        return NoteResponse(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting note {note_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get note")


@router.delete(
    "/{note_id}",
    status_code=204,
    summary="刪除筆記",
    description="根據 ID 刪除特定筆記"
)
def delete_note(note_id: int) -> None:
    """刪除筆記
    
    Args:
        note_id: 筆記 ID
        
    Raises:
        HTTPException: 當筆記不存在時
    """
    try:
        # 先檢查筆記是否存在
        row = db.get_note(note_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # 執行刪除（需要在 db 模組中新增此函式）
        # 這裡暫時使用直接 SQL
        from ..db import get_connection
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            connection.commit()
        
        logger.info(f"Note deleted: id={note_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting note {note_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete note")
