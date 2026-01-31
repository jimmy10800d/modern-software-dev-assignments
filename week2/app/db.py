from __future__ import annotations  # 延後型別評估

import sqlite3  # SQLite 資料庫
from pathlib import Path  # 路徑處理
from typing import Optional  # Optional 型別

BASE_DIR = Path(__file__).resolve().parents[1]  # 專案基底目錄
DATA_DIR = BASE_DIR / "data"  # 資料目錄
DB_PATH = DATA_DIR / "app.db"  # 資料庫檔案路徑


def ensure_data_directory_exists() -> None:  # 確保資料目錄存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)  # 建立目錄（含父層）


def get_connection() -> sqlite3.Connection:  # 取得資料庫連線
    ensure_data_directory_exists()  # 確保資料目錄存在
    connection = sqlite3.connect(DB_PATH)  # 建立 SQLite 連線
    connection.row_factory = sqlite3.Row  # 讓查詢結果可用欄位名稱存取
    return connection  # 回傳連線


def init_db() -> None:  # 初始化資料庫結構
    ensure_data_directory_exists()  # 確保資料目錄存在
    with get_connection() as connection:  # 開啟連線
        cursor = connection.cursor()  # 建立游標
        cursor.execute(  # 建立 notes 表
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """
        )
        cursor.execute(  # 建立 action_items 表
            """
            CREATE TABLE IF NOT EXISTS action_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                text TEXT NOT NULL,
                done INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (note_id) REFERENCES notes(id)
            );
            """
        )
        connection.commit()  # 提交變更


def insert_note(content: str) -> int:  # 新增筆記
    with get_connection() as connection:  # 開啟連線
        cursor = connection.cursor()  # 建立游標
        cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))  # 插入資料
        connection.commit()  # 提交變更
        return int(cursor.lastrowid)  # 回傳新增的 id


def list_notes() -> list[sqlite3.Row]:  # 列出所有筆記
    with get_connection() as connection:  # 開啟連線
        cursor = connection.cursor()  # 建立游標
        cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")  # 查詢資料
        return list(cursor.fetchall())  # 回傳結果清單


def get_note(note_id: int) -> Optional[sqlite3.Row]:  # 取得單一筆記
    with get_connection() as connection:  # 開啟連線
        cursor = connection.cursor()  # 建立游標
        cursor.execute(  # 查詢指定 id 的筆記
            "SELECT id, content, created_at FROM notes WHERE id = ?",
            (note_id,),
        )
        row = cursor.fetchone()  # 取第一筆
        return row  # 回傳結果或 None


def insert_action_items(items: list[str], note_id: Optional[int] = None) -> list[int]:  # 新增行動項目
    with get_connection() as connection:  # 開啟連線
        cursor = connection.cursor()  # 建立游標
        ids: list[int] = []  # 記錄新增的 id
        for item in items:  # 逐一插入
            cursor.execute(  # 插入行動項目
                "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                (note_id, item),
            )
            ids.append(int(cursor.lastrowid))  # 收集 id
        connection.commit()  # 提交變更
        return ids  # 回傳新增 id 清單


def list_action_items(note_id: Optional[int] = None) -> list[sqlite3.Row]:  # 列出行動項目
    with get_connection() as connection:  # 開啟連線
        cursor = connection.cursor()  # 建立游標
        if note_id is None:  # 若未指定 note_id
            cursor.execute(  # 查詢全部行動項目
                "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
            )
        else:  # 若指定 note_id
            cursor.execute(  # 查詢指定筆記的行動項目
                "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                (note_id,),
            )
        return list(cursor.fetchall())  # 回傳結果


def mark_action_item_done(action_item_id: int, done: bool) -> None:  # 更新完成狀態
    with get_connection() as connection:  # 開啟連線
        cursor = connection.cursor()  # 建立游標
        cursor.execute(  # 更新 done 欄位
            "UPDATE action_items SET done = ? WHERE id = ?",
            (1 if done else 0, action_item_id),
        )
        connection.commit()  # 提交變更


