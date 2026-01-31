from typing import Optional  # Optional 型別

from fastapi import APIRouter, Depends, HTTPException  # FastAPI 路由與相依注入
from sqlalchemy import select  # SQLAlchemy 查詢
from sqlalchemy.orm import Session  # Session 型別

from ..db import get_db  # 取得 DB Session
from ..models import Note  # ORM 模型
from ..schemas import NoteCreate, NoteRead  # Pydantic schema

router = APIRouter(prefix="/notes", tags=["notes"])  # 路由設定


@router.get("/", response_model=list[NoteRead])  # 列出筆記
def list_notes(db: Session = Depends(get_db)) -> list[NoteRead]:  # 取得清單
    rows = db.execute(select(Note)).scalars().all()  # 查詢全部
    return [NoteRead.model_validate(row) for row in rows]  # 轉成 schema


@router.post("/", response_model=NoteRead, status_code=201)  # 新增筆記
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:  # 建立
    note = Note(title=payload.title, content=payload.content)  # 建立模型
    db.add(note)  # 加入 session
    db.flush()  # 同步
    db.refresh(note)  # 刷新
    return NoteRead.model_validate(note)  # 回傳結果


@router.get("/search/", response_model=list[NoteRead])  # 搜尋筆記
def search_notes(q: Optional[str] = None, db: Session = Depends(get_db)) -> list[NoteRead]:  # 搜尋
    if not q:  # 若未提供查詢
        rows = db.execute(select(Note)).scalars().all()  # 查詢全部
    else:
        rows = (  # 查詢符合關鍵字
            db.execute(select(Note).where((Note.title.contains(q)) | (Note.content.contains(q))))
            .scalars()
            .all()
        )
    return [NoteRead.model_validate(row) for row in rows]  # 回傳結果


@router.get("/{note_id}", response_model=NoteRead)  # 取得單筆筆記
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:  # 取得
    note = db.get(Note, note_id)  # 查詢資料
    if not note:  # 若不存在
        raise HTTPException(status_code=404, detail="Note not found")  # 回傳錯誤
    return NoteRead.model_validate(note)  # 回傳結果
