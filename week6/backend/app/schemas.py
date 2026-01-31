from datetime import datetime  # 日期時間

from pydantic import BaseModel  # Pydantic 基底模型


class NoteCreate(BaseModel):  # 建立筆記輸入
    title: str  # 標題
    content: str  # 內容


class NoteRead(BaseModel):  # 讀取筆記輸出
    id: int  # id
    title: str  # 標題
    content: str  # 內容
    created_at: datetime  # 建立時間
    updated_at: datetime  # 更新時間

    class Config:  # Pydantic 設定
        from_attributes = True  # 允許從 ORM 讀取


class NotePatch(BaseModel):  # 更新筆記輸入
    title: str | None = None  # 標題（可選）
    content: str | None = None  # 內容（可選）


class ActionItemCreate(BaseModel):  # 建立行動項目輸入
    description: str  # 描述


class ActionItemRead(BaseModel):  # 讀取行動項目輸出
    id: int  # id
    description: str  # 描述
    completed: bool  # 完成狀態
    created_at: datetime  # 建立時間
    updated_at: datetime  # 更新時間

    class Config:  # Pydantic 設定
        from_attributes = True  # 允許從 ORM 讀取


class ActionItemPatch(BaseModel):  # 更新行動項目輸入
    description: str | None = None  # 描述（可選）
    completed: bool | None = None  # 完成狀態（可選）


