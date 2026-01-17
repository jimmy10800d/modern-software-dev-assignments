import os
import sys
import tempfile
from collections.abc import Generator

from pathlib import Path

# Ensure `import backend...` resolves to THIS week's backend package even when running from repo root.
# week6/backend/tests/conftest.py -> parents[2] is week6/
_WEEK_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_WEEK_DIR))

_THIS_CONFTEST = Path(__file__).resolve()
for _name, _mod in list(sys.modules.items()):
    if not (_name == "backend" or _name.startswith("backend.")):
        continue
    _mod_file = getattr(_mod, "__file__", None)
    if _mod_file and Path(_mod_file).resolve() == _THIS_CONFTEST:
        continue
    if _name.endswith(".tests.conftest"):
        continue
    del sys.modules[_name]

import pytest
from backend.app.db import get_db
from backend.app.main import app
from backend.app.models import Base
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)

    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
        os.unlink(db_path)


