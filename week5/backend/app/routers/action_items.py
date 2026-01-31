from fastapi import APIRouter, Depends, HTTPException  # FastAPI 路由與相依注入
from sqlalchemy import select  # SQLAlchemy 查詢
from sqlalchemy.orm import Session  # Session 型別

from ..db import get_db  # 取得 DB Session
from ..models import ActionItem  # ORM 模型
from ..schemas import ActionItemCreate, ActionItemRead  # Pydantic schema

router = APIRouter(prefix="/action-items", tags=["action_items"])  # 路由設定


@router.get("/", response_model=list[ActionItemRead])  # 列出行動項目
def list_items(db: Session = Depends(get_db)) -> list[ActionItemRead]:  # 取得清單
    rows = db.execute(select(ActionItem)).scalars().all()  # 查詢全部
    return [ActionItemRead.model_validate(row) for row in rows]  # 轉成 schema


@router.post("/", response_model=ActionItemRead, status_code=201)  # 新增行動項目
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:  # 建立
    item = ActionItem(description=payload.description, completed=False)  # 建立模型
    db.add(item)  # 加入 session
    db.flush()  # 同步
    db.refresh(item)  # 刷新
    return ActionItemRead.model_validate(item)  # 回傳結果


@router.put("/{item_id}/complete", response_model=ActionItemRead)  # 完成行動項目
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:  # 更新完成
    item = db.get(ActionItem, item_id)  # 查詢項目
    if not item:  # 若不存在
        raise HTTPException(status_code=404, detail="Action item not found")  # 回傳錯誤
    item.completed = True  # 設定完成
    db.add(item)  # 加入 session
    db.flush()  # 同步
    db.refresh(item)  # 刷新
    return ActionItemRead.model_validate(item)  # 回傳結果
