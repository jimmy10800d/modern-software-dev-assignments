"""
Week 2 - Pydantic Schemas（API 請求/回應模型）

TODO 3: 重構 - 定義清晰的 API 契約
這個檔案定義所有 API 端點的請求和回應格式，
使用 Pydantic 模型來確保資料驗證和類型安全。
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================================
# Note 相關 Schemas
# ============================================================================

class NoteCreate(BaseModel):
    """建立筆記的請求格式"""
    content: str = Field(..., min_length=1, description="筆記內容，不可為空")


class NoteResponse(BaseModel):
    """筆記的回應格式"""
    id: int = Field(..., description="筆記 ID")
    content: str = Field(..., description="筆記內容")
    created_at: str = Field(..., description="建立時間")


class NoteListResponse(BaseModel):
    """筆記列表的回應格式"""
    notes: List[NoteResponse] = Field(default_factory=list, description="筆記清單")
    total: int = Field(..., description="總筆數")


# ============================================================================
# Action Item 相關 Schemas
# ============================================================================

class ActionItemResponse(BaseModel):
    """單一行動項目的回應格式"""
    id: int = Field(..., description="行動項目 ID")
    text: str = Field(..., description="行動項目內容")
    note_id: Optional[int] = Field(None, description="關聯的筆記 ID")
    done: bool = Field(False, description="是否已完成")
    created_at: Optional[str] = Field(None, description="建立時間")


class ExtractRequest(BaseModel):
    """抽取行動項目的請求格式"""
    text: str = Field(..., min_length=1, description="要抽取的文字內容")
    save_note: bool = Field(False, description="是否儲存為筆記")


class ExtractLLMRequest(BaseModel):
    """LLM 抽取行動項目的請求格式"""
    text: str = Field(..., min_length=1, description="要抽取的文字內容")
    save_note: bool = Field(False, description="是否儲存為筆記")
    model: str = Field("llama3.1:8b", description="使用的 LLM 模型")


class ExtractResponse(BaseModel):
    """抽取行動項目的回應格式"""
    note_id: Optional[int] = Field(None, description="儲存的筆記 ID（若有儲存）")
    items: List[ActionItemResponse] = Field(default_factory=list, description="抽取的行動項目")


class MarkDoneRequest(BaseModel):
    """標記完成狀態的請求格式"""
    done: bool = Field(True, description="完成狀態")


class MarkDoneResponse(BaseModel):
    """標記完成狀態的回應格式"""
    id: int = Field(..., description="行動項目 ID")
    done: bool = Field(..., description="更新後的完成狀態")


# ============================================================================
# 錯誤回應 Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """錯誤回應格式"""
    detail: str = Field(..., description="錯誤訊息")
