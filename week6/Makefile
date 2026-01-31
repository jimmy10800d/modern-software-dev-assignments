.PHONY: run test format lint seed # 宣告虛擬目標

run: # 啟動伺服器
	PYTHONPATH=. uvicorn backend.app.main:app --reload --host $${HOST:-127.0.0.1} --port $${PORT:-8000} # 執行 FastAPI

test: # 執行測試
	PYTHONPATH=. pytest -q backend/tests # 跑 pytest

format: # 格式化程式碼
	black . # Black 格式化
	ruff check . --fix # Ruff 自動修正

lint: # 程式碼檢查
	ruff check . # Ruff 檢查

seed: # 套用 seed 資料
	PYTHONPATH=. python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()" # 執行 seed


