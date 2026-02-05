from __future__ import annotations  # 延後型別評估

from typing import Any, Dict, List, Optional  # 型別註解

from fastapi import APIRouter, HTTPException  # FastAPI 路由與錯誤

from .. import db  # 資料庫操作
from ..services.extract import extract_action_items, extract_action_items_llm  # 行動項目抽取（規則版 + LLM 版）
from ..schemas import (  # TODO 3: 使用 Pydantic schemas
    ExtractRequest,
    ExtractLLMRequest,
    ExtractResponse,
    ActionItemResponse,
    MarkDoneRequest,
    MarkDoneResponse,
)


router = APIRouter(prefix="/action-items", tags=["action-items"])  # 設定路由前綴與標籤


# ============================================================================
# TODO 3: 重構 - 使用 Pydantic schema 定義請求/回應格式
# ============================================================================

@router.post("/extract", response_model=ExtractResponse)  # 建立抽取行動項目的 API
def extract(payload: ExtractRequest) -> ExtractResponse:  # 使用 Pydantic 模型驗證請求
    """
    使用規則式方法抽取行動項目。
    
    - 從文字中識別子彈符號、關鍵字前綴、勾選框等格式
    - 可選擇是否將原文儲存為筆記
    """
    text = payload.text.strip()  # 取得文字內容
    if not text:  # 若為空
        raise HTTPException(status_code=400, detail="text is required")  # 回傳錯誤

    note_id: Optional[int] = None  # 預設不儲存筆記
    if payload.save_note:  # 若要求儲存筆記
        note_id = db.insert_note(text)  # 新增筆記並取得 id

    items = extract_action_items(text)  # 抽取行動項目
    ids = db.insert_action_items(items, note_id=note_id)  # 儲存行動項目
    
    return ExtractResponse(
        note_id=note_id,
        items=[ActionItemResponse(id=i, text=t) for i, t in zip(ids, items)]
    )


# ============================================================================
# TODO 4: 新增 LLM 抽取端點
# ============================================================================

@router.post("/extract-llm", response_model=ExtractResponse)  # LLM 版抽取 API
def extract_llm(payload: ExtractLLMRequest) -> ExtractResponse:
    """
    使用 LLM（大型語言模型）抽取行動項目。
    
    - 透過 Ollama 呼叫本地 LLM 模型
    - 可指定使用的模型（預設 llama3.1:8b）
    - 更智慧地理解語意並抽取待辦事項
    """
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(text)

    try:
        items = extract_action_items_llm(text, model=payload.model)  # 使用 LLM 抽取
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM extraction failed: {str(e)}")

    ids = db.insert_action_items(items, note_id=note_id)
    
    return ExtractResponse(
        note_id=note_id,
        items=[ActionItemResponse(id=i, text=t) for i, t in zip(ids, items)]
    )


@router.get("", response_model=List[ActionItemResponse])  # 取得行動項目列表
def list_all(note_id: Optional[int] = None) -> List[ActionItemResponse]:  # 可指定 note_id 篩選
    """
    列出所有行動項目，可選擇依筆記 ID 篩選。
    """
    rows = db.list_action_items(note_id=note_id)  # 查詢資料
    return [  # 組合回傳結構
        ActionItemResponse(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)  # 更新完成狀態
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> MarkDoneResponse:  # 處理更新
    """
    標記行動項目的完成狀態。
    """
    db.mark_action_item_done(action_item_id, payload.done)  # 更新資料庫
    return MarkDoneResponse(id=action_item_id, done=payload.done)  # 回傳結果


