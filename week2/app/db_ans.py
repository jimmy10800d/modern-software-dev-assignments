"""
Week2 TODO 3 解答：重構資料庫層
db_ans.py - 改進錯誤處理、型別安全、資源管理
"""
from __future__ import annotations  # 延後型別評估

import sqlite3  # SQLite 資料庫
from pathlib import Path  # 路徑處理
from typing import Optional, List, Dict, Any, Generator  # 型別註解
from contextlib import contextmanager  # 上下文管理器
from dataclasses import dataclass  # 資料類別
from datetime import datetime  # 時間處理
import logging  # 日誌模組

# ============================================================
# 設定日誌
# ============================================================

logger = logging.getLogger(__name__)  # 建立日誌器

# ============================================================
# 路徑配置
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]  # 專案基底目錄
DATA_DIR = BASE_DIR / "data"  # 資料目錄
DB_PATH = DATA_DIR / "app.db"  # 資料庫檔案路徑


# ============================================================
# 資料模型（Data Classes）
# ============================================================

@dataclass
class Note:
    """筆記資料模型"""
    id: int  # 筆記 ID
    content: str  # 筆記內容
    created_at: str  # 建立時間
    
    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Note":
        """從資料庫列建立 Note 物件"""
        return cls(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "content": self.content,
            "created_at": self.created_at
        }


@dataclass
class ActionItem:
    """行動項目資料模型"""
    id: int  # 項目 ID
    note_id: Optional[int]  # 關聯的筆記 ID（可為空）
    text: str  # 項目文字
    done: bool  # 是否完成
    created_at: str  # 建立時間
    
    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "ActionItem":
        """從資料庫列建立 ActionItem 物件"""
        return cls(
            id=row["id"],
            note_id=row["note_id"],
            text=row["text"],
            done=bool(row["done"]),
            created_at=row["created_at"]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "note_id": self.note_id,
            "text": self.text,
            "done": self.done,
            "created_at": self.created_at
        }


# ============================================================
# 自定義例外
# ============================================================

class DatabaseError(Exception):
    """資料庫操作錯誤的基礎例外"""
    pass


class NoteNotFoundError(DatabaseError):
    """筆記不存在錯誤"""
    def __init__(self, note_id: int):
        self.note_id = note_id
        super().__init__(f"Note with id {note_id} not found")


class ActionItemNotFoundError(DatabaseError):
    """行動項目不存在錯誤"""
    def __init__(self, action_item_id: int):
        self.action_item_id = action_item_id
        super().__init__(f"ActionItem with id {action_item_id} not found")


# ============================================================
# 資料庫連線管理
# ============================================================

def ensure_data_directory_exists() -> None:
    """確保資料目錄存在
    
    建立 data 目錄（若不存在），包含所有父目錄。
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)  # 建立目錄（含父層）
    logger.debug(f"Data directory ensured: {DATA_DIR}")


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """取得資料庫連線的上下文管理器
    
    使用上下文管理器確保連線正確關閉。
    
    Yields:
        sqlite3.Connection: SQLite 連線物件
        
    Raises:
        DatabaseError: 當無法建立連線時
    """
    ensure_data_directory_exists()  # 確保資料目錄存在
    connection = None
    try:
        connection = sqlite3.connect(DB_PATH)  # 建立 SQLite 連線
        connection.row_factory = sqlite3.Row  # 讓查詢結果可用欄位名稱存取
        connection.execute("PRAGMA foreign_keys = ON")  # 啟用外鍵約束
        logger.debug(f"Database connection established: {DB_PATH}")
        yield connection  # 提供連線給呼叫者
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise DatabaseError(f"Failed to connect to database: {e}")
    finally:
        if connection:
            connection.close()  # 關閉連線
            logger.debug("Database connection closed")


@contextmanager
def get_transaction() -> Generator[sqlite3.Connection, None, None]:
    """取得帶交易管理的資料庫連線
    
    自動處理 commit 和 rollback。
    
    Yields:
        sqlite3.Connection: SQLite 連線物件
    """
    with get_connection() as connection:
        try:
            yield connection  # 提供連線
            connection.commit()  # 成功則提交
            logger.debug("Transaction committed")
        except Exception as e:
            connection.rollback()  # 失敗則回滾
            logger.error(f"Transaction rolled back: {e}")
            raise


# ============================================================
# 資料庫初始化
# ============================================================

def init_db() -> None:
    """初始化資料庫結構
    
    建立必要的資料表（若不存在）。
    """
    ensure_data_directory_exists()  # 確保資料目錄存在
    
    with get_transaction() as connection:
        cursor = connection.cursor()
        
        # 建立 notes 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)
        
        # 建立 action_items 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE SET NULL
            );
        """)
        
        # 建立索引以加速查詢
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_action_items_note_id 
            ON action_items(note_id);
        """)
        
        logger.info("Database initialized successfully")


def reset_db() -> None:
    """重置資料庫（刪除所有資料）
    
    主要用於測試目的。
    """
    with get_transaction() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM action_items")
        cursor.execute("DELETE FROM notes")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('notes', 'action_items')")
        logger.warning("Database reset completed")


# ============================================================
# Notes CRUD 操作
# ============================================================

def insert_note(content: str) -> Note:
    """新增筆記
    
    Args:
        content: 筆記內容
        
    Returns:
        Note: 新建立的筆記物件
        
    Raises:
        ValueError: 當 content 為空時
        DatabaseError: 當資料庫操作失敗時
    """
    if not content or not content.strip():
        raise ValueError("Note content cannot be empty")
    
    content = content.strip()  # 清理空白
    
    with get_transaction() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO notes (content) VALUES (?)",
            (content,)
        )
        note_id = cursor.lastrowid
        
        # 取得完整的筆記資料
        cursor.execute(
            "SELECT id, content, created_at FROM notes WHERE id = ?",
            (note_id,)
        )
        row = cursor.fetchone()
        
        logger.info(f"Note created with id: {note_id}")
        return Note.from_row(row)


def list_notes(
    limit: Optional[int] = None,
    offset: int = 0
) -> List[Note]:
    """列出所有筆記
    
    Args:
        limit: 最大回傳數量（可選）
        offset: 跳過的筆數
        
    Returns:
        List[Note]: 筆記列表
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        
        query = "SELECT id, content, created_at FROM notes ORDER BY id DESC"
        params: List[Any] = []
        
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [Note.from_row(row) for row in rows]


def get_note(note_id: int) -> Note:
    """取得單一筆記
    
    Args:
        note_id: 筆記 ID
        
    Returns:
        Note: 筆記物件
        
    Raises:
        NoteNotFoundError: 當筆記不存在時
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, content, created_at FROM notes WHERE id = ?",
            (note_id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            raise NoteNotFoundError(note_id)
        
        return Note.from_row(row)


def update_note(note_id: int, content: str) -> Note:
    """更新筆記內容
    
    Args:
        note_id: 筆記 ID
        content: 新的筆記內容
        
    Returns:
        Note: 更新後的筆記物件
        
    Raises:
        ValueError: 當 content 為空時
        NoteNotFoundError: 當筆記不存在時
    """
    if not content or not content.strip():
        raise ValueError("Note content cannot be empty")
    
    content = content.strip()
    
    with get_transaction() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE notes SET content = ? WHERE id = ?",
            (content, note_id)
        )
        
        if cursor.rowcount == 0:
            raise NoteNotFoundError(note_id)
        
        cursor.execute(
            "SELECT id, content, created_at FROM notes WHERE id = ?",
            (note_id,)
        )
        row = cursor.fetchone()
        
        logger.info(f"Note updated: {note_id}")
        return Note.from_row(row)


def delete_note(note_id: int) -> bool:
    """刪除筆記
    
    Args:
        note_id: 筆記 ID
        
    Returns:
        bool: 是否成功刪除
        
    Raises:
        NoteNotFoundError: 當筆記不存在時
    """
    with get_transaction() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM notes WHERE id = ?",
            (note_id,)
        )
        
        if cursor.rowcount == 0:
            raise NoteNotFoundError(note_id)
        
        logger.info(f"Note deleted: {note_id}")
        return True


# ============================================================
# ActionItems CRUD 操作
# ============================================================

def insert_action_items(
    items: List[str],
    note_id: Optional[int] = None
) -> List[ActionItem]:
    """新增多個行動項目
    
    Args:
        items: 行動項目文字列表
        note_id: 關聯的筆記 ID（可選）
        
    Returns:
        List[ActionItem]: 新建立的行動項目列表
        
    Raises:
        NoteNotFoundError: 當指定的 note_id 不存在時
    """
    if not items:
        return []
    
    # 驗證 note_id 存在（若有提供）
    if note_id is not None:
        try:
            get_note(note_id)
        except NoteNotFoundError:
            raise
    
    created_items: List[ActionItem] = []
    
    with get_transaction() as connection:
        cursor = connection.cursor()
        
        for item_text in items:
            text = item_text.strip()
            if not text:
                continue
            
            cursor.execute(
                "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                (note_id, text)
            )
            
            item_id = cursor.lastrowid
            
            cursor.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
                (item_id,)
            )
            row = cursor.fetchone()
            created_items.append(ActionItem.from_row(row))
        
        logger.info(f"Created {len(created_items)} action items")
        return created_items


def list_action_items(
    note_id: Optional[int] = None,
    done: Optional[bool] = None,
    limit: Optional[int] = None,
    offset: int = 0
) -> List[ActionItem]:
    """列出行動項目
    
    Args:
        note_id: 篩選指定筆記的行動項目
        done: 篩選完成/未完成的項目
        limit: 最大回傳數量
        offset: 跳過的筆數
        
    Returns:
        List[ActionItem]: 行動項目列表
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        
        query = "SELECT id, note_id, text, done, created_at FROM action_items"
        conditions: List[str] = []
        params: List[Any] = []
        
        if note_id is not None:
            conditions.append("note_id = ?")
            params.append(note_id)
        
        if done is not None:
            conditions.append("done = ?")
            params.append(1 if done else 0)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY id DESC"
        
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [ActionItem.from_row(row) for row in rows]


def get_action_item(action_item_id: int) -> ActionItem:
    """取得單一行動項目
    
    Args:
        action_item_id: 行動項目 ID
        
    Returns:
        ActionItem: 行動項目物件
        
    Raises:
        ActionItemNotFoundError: 當行動項目不存在時
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
            (action_item_id,)
        )
        row = cursor.fetchone()
        
        if row is None:
            raise ActionItemNotFoundError(action_item_id)
        
        return ActionItem.from_row(row)


def mark_action_item_done(action_item_id: int, done: bool) -> ActionItem:
    """更新行動項目完成狀態
    
    Args:
        action_item_id: 行動項目 ID
        done: 完成狀態
        
    Returns:
        ActionItem: 更新後的行動項目物件
        
    Raises:
        ActionItemNotFoundError: 當行動項目不存在時
    """
    with get_transaction() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE action_items SET done = ? WHERE id = ?",
            (1 if done else 0, action_item_id)
        )
        
        if cursor.rowcount == 0:
            raise ActionItemNotFoundError(action_item_id)
        
        cursor.execute(
            "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
            (action_item_id,)
        )
        row = cursor.fetchone()
        
        logger.info(f"ActionItem {action_item_id} marked as {'done' if done else 'not done'}")
        return ActionItem.from_row(row)


def delete_action_item(action_item_id: int) -> bool:
    """刪除行動項目
    
    Args:
        action_item_id: 行動項目 ID
        
    Returns:
        bool: 是否成功刪除
        
    Raises:
        ActionItemNotFoundError: 當行動項目不存在時
    """
    with get_transaction() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM action_items WHERE id = ?",
            (action_item_id,)
        )
        
        if cursor.rowcount == 0:
            raise ActionItemNotFoundError(action_item_id)
        
        logger.info(f"ActionItem deleted: {action_item_id}")
        return True


# ============================================================
# 統計與輔助函式
# ============================================================

def get_stats() -> Dict[str, Any]:
    """取得資料庫統計資訊
    
    Returns:
        Dict: 包含筆記與行動項目統計的字典
    """
    with get_connection() as connection:
        cursor = connection.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM notes")
        notes_count = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM action_items")
        items_count = cursor.fetchone()["count"]
        
        cursor.execute("SELECT COUNT(*) as count FROM action_items WHERE done = 1")
        done_count = cursor.fetchone()["count"]
        
        return {
            "notes_count": notes_count,
            "action_items_count": items_count,
            "completed_items_count": done_count,
            "pending_items_count": items_count - done_count
        }
