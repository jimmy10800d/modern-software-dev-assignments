"""
Week2 TODO 3 解答：Pydantic Schemas
schemas_ans.py - API 請求與回應的資料結構定義
"""
from __future__ import annotations  # 延後型別評估

from typing import Optional, List  # 型別註解
from datetime import datetime  # 時間處理
from pydantic import BaseModel, Field, field_validator  # Pydantic 驗證


# ============================================================
# Note Schemas（筆記相關）
# ============================================================

class NoteCreate(BaseModel):
    """建立筆記的請求模型"""
    content: str = Field(..., min_length=1, max_length=10000, description="筆記內容")
    
    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        """驗證內容不為空白"""
        if not v.strip():
            raise ValueError("Content cannot be empty or whitespace only")
        return v.strip()


class NoteUpdate(BaseModel):
    """更新筆記的請求模型"""
    content: str = Field(..., min_length=1, max_length=10000, description="新的筆記內容")
    
    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        """驗證內容不為空白"""
        if not v.strip():
            raise ValueError("Content cannot be empty or whitespace only")
        return v.strip()


class NoteResponse(BaseModel):
    """筆記回應模型"""
    id: int = Field(..., description="筆記 ID")
    content: str = Field(..., description="筆記內容")
    created_at: str = Field(..., description="建立時間")

    class Config:
        from_attributes = True  # 支援從 ORM 物件建立


class NoteListResponse(BaseModel):
    """筆記列表回應模型"""
    notes: List[NoteResponse] = Field(default_factory=list, description="筆記列表")
    total: int = Field(0, description="總筆數")


# ============================================================
# ActionItem Schemas（行動項目相關）
# ============================================================

class ActionItemCreate(BaseModel):
    """建立行動項目的請求模型"""
    text: str = Field(..., min_length=1, max_length=500, description="項目文字")
    note_id: Optional[int] = Field(None, description="關聯的筆記 ID")
    
    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        """驗證文字不為空白"""
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


class ActionItemUpdate(BaseModel):
    """更新行動項目的請求模型"""
    text: Optional[str] = Field(None, min_length=1, max_length=500, description="項目文字")
    done: Optional[bool] = Field(None, description="是否完成")
    
    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """驗證文字不為空白"""
        if v is not None and not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip() if v else None


class MarkDoneRequest(BaseModel):
    """標記完成的請求模型"""
    done: bool = Field(True, description="完成狀態")


class ActionItemResponse(BaseModel):
    """行動項目回應模型"""
    id: int = Field(..., description="項目 ID")
    note_id: Optional[int] = Field(None, description="關聯的筆記 ID")
    text: str = Field(..., description="項目文字")
    done: bool = Field(False, description="是否完成")
    created_at: str = Field(..., description="建立時間")

    class Config:
        from_attributes = True


class ActionItemListResponse(BaseModel):
    """行動項目列表回應模型"""
    items: List[ActionItemResponse] = Field(default_factory=list, description="項目列表")
    total: int = Field(0, description="總筆數")


# ============================================================
# Extract Schemas（抽取相關）
# ============================================================

class ExtractRequest(BaseModel):
    """抽取行動項目的請求模型"""
    text: str = Field(..., min_length=1, max_length=50000, description="要分析的文字")
    save_note: bool = Field(False, description="是否儲存為筆記")
    
    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        """驗證文字不為空白"""
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


class ExtractLLMRequest(BaseModel):
    """LLM 抽取行動項目的請求模型"""
    text: str = Field(..., min_length=1, max_length=50000, description="要分析的文字")
    save_note: bool = Field(False, description="是否儲存為筆記")
    model: Optional[str] = Field(None, description="指定 Ollama 模型（可選）")
    
    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        """驗證文字不為空白"""
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


class ExtractedItem(BaseModel):
    """單一抽取項目"""
    id: int = Field(..., description="項目 ID")
    text: str = Field(..., description="項目文字")


class ExtractResponse(BaseModel):
    """抽取結果回應模型"""
    note_id: Optional[int] = Field(None, description="儲存的筆記 ID（若有）")
    items: List[ExtractedItem] = Field(default_factory=list, description="抽取的行動項目")
    method: str = Field("heuristic", description="使用的抽取方法")


# ============================================================
# Health & Stats Schemas（健康檢查與統計）
# ============================================================

class HealthResponse(BaseModel):
    """健康檢查回應模型"""
    status: str = Field("ok", description="服務狀態")
    version: str = Field("1.0.0", description="API 版本")


class StatsResponse(BaseModel):
    """統計資訊回應模型"""
    notes_count: int = Field(0, description="筆記總數")
    action_items_count: int = Field(0, description="行動項目總數")
    completed_items_count: int = Field(0, description="已完成項目數")
    pending_items_count: int = Field(0, description="待辦項目數")


# ============================================================
# Error Schemas（錯誤回應）
# ============================================================

class ErrorResponse(BaseModel):
    """錯誤回應模型"""
    detail: str = Field(..., description="錯誤訊息")
    error_code: Optional[str] = Field(None, description="錯誤代碼")


class ValidationErrorDetail(BaseModel):
    """驗證錯誤詳情"""
    loc: List[str] = Field(default_factory=list, description="錯誤位置")
    msg: str = Field(..., description="錯誤訊息")
    type: str = Field(..., description="錯誤類型")


class ValidationErrorResponse(BaseModel):
    """驗證錯誤回應模型"""
    detail: List[ValidationErrorDetail] = Field(default_factory=list, description="錯誤詳情列表")
