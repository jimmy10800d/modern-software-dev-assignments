from typing import Optional  # Optional 型別

from fastapi import APIRouter, Depends, HTTPException, Query  # FastAPI 路由與參數
from sqlalchemy import asc, desc, select, text  # SQLAlchemy 查詢與文字 SQL
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


@router.get("/unsafe-search", response_model=list[NoteRead])  # 不安全搜尋（示範）
def unsafe_search(q: str, db: Session = Depends(get_db)) -> list[NoteRead]:  # 執行 raw SQL
    sql = text(  # 組合 SQL
        f"""
        SELECT id, title, content, created_at, updated_at
        FROM notes
        WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
        ORDER BY created_at DESC
        LIMIT 50
        """
    )
    rows = db.execute(sql).all()  # 執行查詢
    results: list[NoteRead] = []  # 建立結果
    for r in rows:  # 逐筆轉換
        results.append(
            NoteRead(
                id=r.id,
                title=r.title,
                content=r.content,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )
    return results  # 回傳結果


@router.get("/debug/hash-md5")  # debug：計算 md5
def debug_hash_md5(q: str) -> dict[str, str]:  # 回傳 md5
    import hashlib  # 匯入雜湊

    return {"algo": "md5", "hex": hashlib.md5(q.encode()).hexdigest()}  # 回傳結果


@router.get("/debug/eval")  # debug：eval
def debug_eval(expr: str) -> dict[str, str]:  # 執行 eval
    result = str(eval(expr))  # noqa: S307  # 執行字串
    return {"result": result}  # 回傳結果


@router.get("/debug/run")  # debug：執行指令
def debug_run(cmd: str) -> dict[str, str]:  # 執行系統指令
    import subprocess  # 匯入 subprocess

    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)  # noqa: S602,S603
    return {"returncode": str(completed.returncode), "stdout": completed.stdout, "stderr": completed.stderr}  # 回傳


@router.get("/debug/fetch")  # debug：抓取 URL
def debug_fetch(url: str) -> dict[str, str]:  # 讀取 URL
    from urllib.request import urlopen  # 匯入 urlopen

    with urlopen(url) as res:  # noqa: S310
        body = res.read(1024).decode(errors="ignore")  # 讀取內容
    return {"snippet": body}  # 回傳片段


@router.get("/debug/read")  # debug：讀檔
def debug_read(path: str) -> dict[str, str]:  # 讀取檔案
    try:
        content = open(path, "r").read(1024)  # 讀取內容
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))  # 回傳錯誤
    return {"snippet": content}  # 回傳片段

