from typing import Optional  # Optional 型別

from fastapi import APIRouter, Depends, HTTPException, Query  # FastAPI 路由與參數
from sqlalchemy import asc, desc, select  # SQLAlchemy 查詢與排序
from sqlalchemy.orm import Session  # Session 型別

from ..db import get_db  # 取得 DB Session
from ..models import ActionItem  # ORM 模型
from ..schemas import ActionItemCreate, ActionItemPatch, ActionItemRead  # Pydantic schema

router = APIRouter(prefix="/action-items", tags=["action_items"])  # 路由設定


@router.get("/", response_model=list[ActionItemRead])  # 列出行動項目
def list_items(
    db: Session = Depends(get_db),  # DB Session
    completed: Optional[bool] = None,  # 完成狀態過濾
    skip: int = 0,  # 分頁起始
    limit: int = Query(50, le=200),  # 分頁大小
    sort: str = Query("-created_at"),  # 排序欄位
) -> list[ActionItemRead]:
    stmt = select(ActionItem)  # 建立查詢
    if completed is not None:  # 若有完成狀態
        stmt = stmt.where(ActionItem.completed.is_(completed))  # 加入條件

    sort_field = sort.lstrip("-")  # 取得欄位名
    order_fn = desc if sort.startswith("-") else asc  # 排序方向
    if hasattr(ActionItem, sort_field):  # 若欄位存在
        stmt = stmt.order_by(order_fn(getattr(ActionItem, sort_field)))  # 套用排序
    else:
        stmt = stmt.order_by(desc(ActionItem.created_at))  # 預設排序

    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()  # 查詢結果
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


@router.patch("/{item_id}", response_model=ActionItemRead)  # 部分更新
def patch_item(item_id: int, payload: ActionItemPatch, db: Session = Depends(get_db)) -> ActionItemRead:  # 更新
    item = db.get(ActionItem, item_id)  # 查詢項目
    if not item:  # 若不存在
        raise HTTPException(status_code=404, detail="Action item not found")  # 回傳錯誤
    if payload.description is not None:  # 若有描述
        item.description = payload.description  # 更新描述
    if payload.completed is not None:  # 若有完成狀態
        item.completed = payload.completed  # 更新完成狀態
    db.add(item)  # 加入 session
    db.flush()  # 同步
    db.refresh(item)  # 刷新
    return ActionItemRead.model_validate(item)  # 回傳結果


