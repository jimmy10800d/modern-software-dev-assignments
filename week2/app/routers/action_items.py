from __future__ import annotations  # 延後型別評估

from typing import Any, Dict, List, Optional  # 型別註解

from fastapi import APIRouter, HTTPException  # FastAPI 路由與錯誤

from .. import db  # 資料庫操作
from ..services.extract import extract_action_items  # 行動項目抽取


router = APIRouter(prefix="/action-items", tags=["action-items"])  # 設定路由前綴與標籤


@router.post("/extract")  # 建立抽取行動項目的 API
def extract(payload: Dict[str, Any]) -> Dict[str, Any]:  # 解析請求內容
    text = str(payload.get("text", "")).strip()  # 取得文字內容
    if not text:  # 若為空
        raise HTTPException(status_code=400, detail="text is required")  # 回傳錯誤

    note_id: Optional[int] = None  # 預設不儲存筆記
    if payload.get("save_note"):  # 若要求儲存筆記
        note_id = db.insert_note(text)  # 新增筆記並取得 id

    items = extract_action_items(text)  # 抽取行動項目
    ids = db.insert_action_items(items, note_id=note_id)  # 儲存行動項目
    return {"note_id": note_id, "items": [{"id": i, "text": t} for i, t in zip(ids, items)]}  # 回傳結果


@router.get("")  # 取得行動項目列表
def list_all(note_id: Optional[int] = None) -> List[Dict[str, Any]]:  # 可指定 note_id 篩選
    rows = db.list_action_items(note_id=note_id)  # 查詢資料
    return [  # 組合回傳結構
        {
            "id": r["id"],
            "note_id": r["note_id"],
            "text": r["text"],
            "done": bool(r["done"]),
            "created_at": r["created_at"],
        }
        for r in rows
    ]


@router.post("/{action_item_id}/done")  # 更新完成狀態
def mark_done(action_item_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:  # 處理更新
    done = bool(payload.get("done", True))  # 取得 done 值
    db.mark_action_item_done(action_item_id, done)  # 更新資料庫
    return {"id": action_item_id, "done": done}  # 回傳結果


