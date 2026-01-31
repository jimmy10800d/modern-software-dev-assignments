from pydantic import BaseModel  # Pydantic 基底模型


class NoteCreate(BaseModel):  # 建立筆記的輸入格式
    title: str  # 標題
    content: str  # 內容


class NoteRead(BaseModel):  # 讀取筆記的輸出格式
    id: int  # id
    title: str  # 標題
    content: str  # 內容

    class Config:  # Pydantic 設定
        from_attributes = True  # 允許從 ORM 讀取


class ActionItemCreate(BaseModel):  # 建立行動項目輸入
    description: str  # 描述


class ActionItemRead(BaseModel):  # 讀取行動項目輸出
    id: int  # id
    description: str  # 描述
    completed: bool  # 完成狀態

    class Config:  # Pydantic 設定
        from_attributes = True  # 允許從 ORM 讀取
