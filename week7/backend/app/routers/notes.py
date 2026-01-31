from typing import Optional  # Optional 型別

from fastapi import APIRouter, Depends, HTTPException, Query  # FastAPI 路由與參數
from sqlalchemy import asc, desc, select  # SQLAlchemy 查詢與排序
from sqlalchemy.orm import Session  # Session 型別

from ..db import get_db  # 取得 DB Session
from ..models import Note  # ORM 模型
from ..schemas import NoteCreate, NotePatch, NoteRead  # Pydantic schema

router = APIRouter(prefix="/notes", tags=["notes"])  # 路由設定


@router.get("/", response_model=list[NoteRead])  # 列出筆記
def list_notes(
    db: Session = Depends(get_db),  # DB Session
    q: Optional[str] = None,  # 搜尋關鍵字
    skip: int = 0,  # 分頁起始
    limit: int = Query(50, le=200),  # 分頁大小
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),  # 排序欄位
) -> list[NoteRead]:
    stmt = select(Note)  # 建立查詢
    if q:  # 若有關鍵字
        stmt = stmt.where((Note.title.contains(q)) | (Note.content.contains(q)))  # 加入條件

    sort_field = sort.lstrip("-")  # 取得欄位名
    order_fn = desc if sort.startswith("-") else asc  # 排序方向
    if hasattr(Note, sort_field):  # 若欄位存在
        stmt = stmt.order_by(order_fn(getattr(Note, sort_field)))  # 套用排序
    else:
        stmt = stmt.order_by(desc(Note.created_at))  # 預設排序

    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()  # 查詢結果
    return [NoteRead.model_validate(row) for row in rows]  # 轉成 schema


@router.post("/", response_model=NoteRead, status_code=201)  # 新增筆記
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:  # 建立
    note = Note(title=payload.title, content=payload.content)  # 建立模型
    db.add(note)  # 加入 session
    db.flush()  # 同步
    db.refresh(note)  # 刷新
    return NoteRead.model_validate(note)  # 回傳結果


@router.patch("/{note_id}", response_model=NoteRead)  # 更新筆記
def patch_note(note_id: int, payload: NotePatch, db: Session = Depends(get_db)) -> NoteRead:  # 更新
    note = db.get(Note, note_id)  # 查詢筆記
    if not note:  # 若不存在
        raise HTTPException(status_code=404, detail="Note not found")  # 回傳錯誤
    if payload.title is not None:  # 若有標題
        note.title = payload.title  # 更新標題
    if payload.content is not None:  # 若有內容
        note.content = payload.content  # 更新內容
    db.add(note)  # 加入 session
    db.flush()  # 同步
    db.refresh(note)  # 刷新
    return NoteRead.model_validate(note)  # 回傳結果


@router.get("/{note_id}", response_model=NoteRead)  # 取得單筆筆記
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:  # 取得
    note = db.get(Note, note_id)  # 查詢
    if not note:  # 若不存在
        raise HTTPException(status_code=404, detail="Note not found")  # 回傳錯誤
    return NoteRead.model_validate(note)  # 回傳結果


