import os  # 作業系統模組
from collections.abc import Iterator  # 迭代器型別
from contextlib import contextmanager  # contextmanager 裝飾器
from pathlib import Path  # 路徑處理

from dotenv import load_dotenv  # 載入環境變數
from sqlalchemy import create_engine, text  # SQLAlchemy 引擎與文字 SQL
from sqlalchemy.orm import Session, sessionmaker  # Session 與 sessionmaker

load_dotenv()  # 載入 .env

DEFAULT_DB_PATH = os.getenv("DATABASE_PATH", "./data/app.db")  # 資料庫路徑

engine = create_engine(f"sqlite:///{DEFAULT_DB_PATH}", connect_args={"check_same_thread": False})  # 建立引擎
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Session 工廠


def get_db() -> Iterator[Session]:  # FastAPI 相依注入用 Session
    session: Session = SessionLocal()  # 建立 Session
    try:
        yield session  # 提供 Session
        session.commit()  # 提交
    except Exception:  # noqa: BLE001
        session.rollback()  # 回滾
        raise
    finally:
        session.close()  # 關閉


@contextmanager
def get_session() -> Iterator[Session]:  # 一般用的 context manager
    session = SessionLocal()  # 建立 Session
    try:
        yield session  # 提供 Session
        session.commit()  # 提交
    except Exception:  # noqa: BLE001
        session.rollback()  # 回滾
        raise
    finally:
        session.close()  # 關閉


def apply_seed_if_needed() -> None:  # 若需要就套用 seed 資料
    db_path = Path(DEFAULT_DB_PATH)  # 資料庫路徑
    db_path.parent.mkdir(parents=True, exist_ok=True)  # 確保目錄存在
    newly_created = not db_path.exists()  # 判斷是否新建
    if newly_created:  # 若新建
        db_path.touch()  # 建立空檔

    seed_file = Path("./data/seed.sql")  # seed 檔案
    if newly_created and seed_file.exists():  # 若新建且 seed 存在
        with engine.begin() as conn:  # 開啟交易
            sql = seed_file.read_text()  # 讀取 SQL
            if sql.strip():  # 若有內容
                for statement in [s.strip() for s in sql.split(";") if s.strip()]:  # 拆分語句
                    conn.execute(text(statement))  # 執行語句
