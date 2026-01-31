"""
Week2 TODO 3 & 4 解答：重構行動項目路由
action_items_ans.py - 使用 Pydantic schemas、新增 LLM 抽取端點
"""
from __future__ import annotations  # 延後型別評估

from typing import Any, Dict, List, Optional  # 型別註解
import logging  # 日誌模組

from fastapi import APIRouter, HTTPException, Query  # FastAPI 路由與工具

from .. import db  # 資料庫操作
from ..services.extract import extract_action_items  # 啟發式抽取
from ..schemas_ans import (  # Schema 模組
    ExtractRequest,
    ExtractLLMRequest,
    ExtractResponse,
    ExtractedItem,
    MarkDoneRequest,
    ActionItemResponse,
    ActionItemListResponse,
    ErrorResponse
)

# ============================================================
# 設定
# ============================================================

logger = logging.getLogger(__name__)  # 建立日誌器

router = APIRouter(
    prefix="/action-items",  # 路由前綴
    tags=["action-items"],  # API 文件標籤
    responses={
        404: {"model": ErrorResponse, "description": "Action item not found"},
        400: {"model": ErrorResponse, "description": "Bad request"}
    }
)


# ============================================================
# 啟發式抽取端點（原有功能）
# ============================================================

@router.post(
    "/extract",
    response_model=ExtractResponse,
    summary="抽取行動項目（啟發式）",
    description="使用規則與關鍵字比對從文字中抽取行動項目"
)
def extract(payload: ExtractRequest) -> ExtractResponse:
    """使用啟發式方法抽取行動項目
    
    Args:
        payload: 包含 text 和 save_note 的請求資料
        
    Returns:
        ExtractResponse: 抽取結果
    """
    try:
        text = payload.text.strip()  # 取得並清理文字
        
        if not text:  # 若為空
            raise HTTPException(status_code=400, detail="Text is required")

        note_id: Optional[int] = None  # 預設不儲存筆記
        if payload.save_note:  # 若要求儲存筆記
            note_id = db.insert_note(text)  # 新增筆記並取得 id
            logger.info(f"Note saved with id: {note_id}")

        items = extract_action_items(text)  # 抽取行動項目
        ids = db.insert_action_items(items, note_id=note_id)  # 儲存行動項目
        
        logger.info(f"Extracted {len(items)} action items using heuristic method")
        
        return ExtractResponse(
            note_id=note_id,
            items=[ExtractedItem(id=i, text=t) for i, t in zip(ids, items)],
            method="heuristic"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting action items: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract action items")


# ============================================================
# TODO 4: LLM 抽取端點（新增功能）
# ============================================================

@router.post(
    "/extract-llm",
    response_model=ExtractResponse,
    summary="抽取行動項目（LLM）",
    description="使用大型語言模型（Ollama）從文字中智慧抽取行動項目"
)
def extract_llm(payload: ExtractLLMRequest) -> ExtractResponse:
    """使用 LLM 抽取行動項目
    
    透過 Ollama 呼叫本地 LLM 模型，智慧分析文字並抽取行動項目。
    若 LLM 呼叫失敗，會自動回退到啟發式方法。
    
    Args:
        payload: 包含 text、save_note 和 model 的請求資料
        
    Returns:
        ExtractResponse: 抽取結果
    """
    try:
        text = payload.text.strip()  # 取得並清理文字
        
        if not text:  # 若為空
            raise HTTPException(status_code=400, detail="Text is required")

        note_id: Optional[int] = None  # 預設不儲存筆記
        if payload.save_note:  # 若要求儲存筆記
            note_id = db.insert_note(text)  # 新增筆記並取得 id
            logger.info(f"Note saved with id: {note_id}")

        method = "llm"  # 使用方法標記
        items: List[str] = []
        
        try:
            # 嘗試使用 LLM 抽取
            from ..services.extract_ans import extract_action_items_llm
            items = extract_action_items_llm(text, model=payload.model)
            logger.info(f"LLM extraction successful: {len(items)} items")
        except ImportError:
            # extract_ans 模組不存在，嘗試內建 LLM 函式
            logger.warning("extract_ans module not found, trying inline LLM")
            items = _inline_llm_extract(text, payload.model)
        except Exception as e:
            # LLM 呼叫失敗，回退到啟發式方法
            logger.warning(f"LLM extraction failed, falling back to heuristic: {e}")
            items = extract_action_items(text)
            method = "heuristic_fallback"
        
        ids = db.insert_action_items(items, note_id=note_id)  # 儲存行動項目
        
        logger.info(f"Extracted {len(items)} action items using {method}")
        
        return ExtractResponse(
            note_id=note_id,
            items=[ExtractedItem(id=i, text=t) for i, t in zip(ids, items)],
            method=method
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in LLM extraction: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract action items")


def _inline_llm_extract(text: str, model: Optional[str] = None) -> List[str]:
    """內建的 LLM 抽取函式
    
    當 extract_ans 模組不存在時使用。
    """
    import os
    import json
    
    model_name = model or os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    
    try:
        from ollama import chat
        
        response = chat(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "Extract action items from the text. Return a JSON object with 'action_items' array."
                },
                {
                    "role": "user",
                    "content": f"Extract action items from:\n\n{text}"
                }
            ]
        )
        
        content = response.message.content
        parsed = json.loads(content)
        
        if isinstance(parsed, dict) and "action_items" in parsed:
            return [str(item).strip() for item in parsed["action_items"] if item]
        
        return []
        
    except Exception as e:
        logger.error(f"Inline LLM extraction failed: {e}")
        raise


# ============================================================
# 列表與狀態更新端點
# ============================================================

@router.get(
    "",
    response_model=ActionItemListResponse,
    summary="列出行動項目",
    description="取得所有或特定筆記的行動項目列表"
)
def list_all(
    note_id: Optional[int] = Query(None, description="篩選特定筆記的項目"),
    done: Optional[bool] = Query(None, description="篩選完成/未完成項目"),
    limit: int = Query(100, ge=1, le=1000, description="回傳筆數上限"),
    offset: int = Query(0, ge=0, description="跳過筆數")
) -> ActionItemListResponse:
    """列出行動項目
    
    Args:
        note_id: 篩選指定筆記的行動項目
        done: 篩選完成/未完成的項目
        limit: 最大回傳數量
        offset: 跳過的筆數
        
    Returns:
        ActionItemListResponse: 行動項目列表
    """
    try:
        rows = db.list_action_items(note_id=note_id)  # 查詢資料
        
        # 應用 done 篩選
        if done is not None:
            rows = [r for r in rows if bool(r["done"]) == done]
        
        # 應用分頁
        total = len(rows)
        paginated = rows[offset:offset + limit]
        
        items = [
            ActionItemResponse(
                id=r["id"],
                note_id=r["note_id"],
                text=r["text"],
                done=bool(r["done"]),
                created_at=r["created_at"]
            )
            for r in paginated
        ]
        
        return ActionItemListResponse(items=items, total=total)
        
    except Exception as e:
        logger.error(f"Error listing action items: {e}")
        raise HTTPException(status_code=500, detail="Failed to list action items")


@router.post(
    "/{action_item_id}/done",
    response_model=ActionItemResponse,
    summary="更新完成狀態",
    description="標記行動項目為已完成或未完成"
)
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> ActionItemResponse:
    """更新行動項目完成狀態
    
    Args:
        action_item_id: 行動項目 ID
        payload: 包含 done 狀態的請求資料
        
    Returns:
        ActionItemResponse: 更新後的行動項目資料
    """
    try:
        db.mark_action_item_done(action_item_id, payload.done)  # 更新資料庫
        
        # 取得更新後的資料
        rows = db.list_action_items()
        item = next((r for r in rows if r["id"] == action_item_id), None)
        
        if item is None:
            raise HTTPException(status_code=404, detail="Action item not found")
        
        logger.info(f"Action item {action_item_id} marked as {'done' if payload.done else 'not done'}")
        
        return ActionItemResponse(
            id=item["id"],
            note_id=item["note_id"],
            text=item["text"],
            done=bool(item["done"]),
            created_at=item["created_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating action item {action_item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update action item")


@router.delete(
    "/{action_item_id}",
    status_code=204,
    summary="刪除行動項目",
    description="刪除指定的行動項目"
)
def delete_action_item(action_item_id: int) -> None:
    """刪除行動項目
    
    Args:
        action_item_id: 行動項目 ID
    """
    try:
        # 檢查是否存在
        rows = db.list_action_items()
        item = next((r for r in rows if r["id"] == action_item_id), None)
        
        if item is None:
            raise HTTPException(status_code=404, detail="Action item not found")
        
        # 執行刪除
        from ..db import get_connection
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM action_items WHERE id = ?", (action_item_id,))
            connection.commit()
        
        logger.info(f"Action item deleted: id={action_item_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting action item {action_item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete action item")
