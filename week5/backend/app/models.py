from sqlalchemy import Boolean, Column, Integer, String, Text  # SQLAlchemy 欄位型別
from sqlalchemy.orm import declarative_base  # ORM 基底

Base = declarative_base()  # 建立 ORM Base


class Note(Base):  # 筆記資料表
    __tablename__ = "notes"  # 表名

    id = Column(Integer, primary_key=True, index=True)  # 主鍵 id
    title = Column(String(200), nullable=False)  # 標題
    content = Column(Text, nullable=False)  # 內容


class ActionItem(Base):  # 行動項目資料表
    __tablename__ = "action_items"  # 表名

    id = Column(Integer, primary_key=True, index=True)  # 主鍵 id
    description = Column(Text, nullable=False)  # 描述
    completed = Column(Boolean, default=False, nullable=False)  # 完成狀態
