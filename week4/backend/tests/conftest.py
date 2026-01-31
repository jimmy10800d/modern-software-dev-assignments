import os  # 作業系統模組
import sys  # 系統模組
import tempfile  # 暫存檔
from collections.abc import Generator  # 產生器型別

from pathlib import Path  # 路徑處理

# Ensure `import backend...` resolves to THIS week's backend package even when running from repo root.
# week4/backend/tests/conftest.py -> parents[2] is week4/
_WEEK_DIR = Path(__file__).resolve().parents[2]  # week4 根目錄
sys.path.insert(0, str(_WEEK_DIR))  # 加入 sys.path

# If other weeks' tests were imported first, `backend` may already be in sys.modules.
# Purge it so this week's `backend` package is imported from `_WEEK_DIR`.
_THIS_CONFTEST = Path(__file__).resolve()  # 本檔案路徑
for _name, _mod in list(sys.modules.items()):  # 走訪已載入模組
    if not (_name == "backend" or _name.startswith("backend.")):  # 只處理 backend
        continue
    _mod_file = getattr(_mod, "__file__", None)  # 取得模組檔案
    if _mod_file and Path(_mod_file).resolve() == _THIS_CONFTEST:  # 跳過自己
        continue
    if _name.endswith(".tests.conftest"):  # 跳過測試 conftest
        continue
    del sys.modules[_name]  # 移除已載入模組

import pytest  # pytest
from backend.app.db import get_db  # 取得 DB 相依
from backend.app.main import app  # FastAPI app
from backend.app.models import Base  # ORM Base
from fastapi.testclient import TestClient  # 測試用 Client
from sqlalchemy import create_engine  # SQLAlchemy 引擎
from sqlalchemy.orm import sessionmaker  # session maker


@pytest.fixture()  # pytest fixture
def client() -> Generator[TestClient, None, None]:  # 回傳測試用 client
    db_fd, db_path = tempfile.mkstemp()  # 建立暫存 DB
    os.close(db_fd)  # 關閉檔案描述符

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})  # 建立引擎
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Session 工廠
    Base.metadata.create_all(bind=engine)  # 建立表格

    def override_get_db():  # 覆寫 get_db
        session = TestingSessionLocal()  # 建立 session
        try:
            yield session  # 提供 session
            session.commit()  # 提交
        except Exception:
            session.rollback()  # 回滾
            raise
        finally:
            session.close()  # 關閉

    app.dependency_overrides[get_db] = override_get_db  # 注入覆寫

    try:
        with TestClient(app) as c:  # 建立測試 client
            yield c  # 回傳 client
    finally:
        app.dependency_overrides.clear()  # 清除覆寫
        engine.dispose()  # 釋放引擎
        os.unlink(db_path)  # 刪除暫存 DB
