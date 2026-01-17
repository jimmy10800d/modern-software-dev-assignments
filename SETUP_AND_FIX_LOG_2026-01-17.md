# Setup & Fix Log (2026-01-17)

本檔案記錄在 Windows + VS Code 環境中，為本 repo 建立 Python/Poetry/Conda 開發環境，以及修復 `pytest` 在 repo root 執行時的收集（collection）錯誤的完整過程。

---

## 1) Git remote（推到自己的 repo）

- 觀察到原本 `origin` 指向課程 repo：`https://github.com/mihail911/modern-software-dev-assignments.git`
- 你的 repo URL：`https://github.com/jimmy10800d/modern-software-dev-assignments.git`
- 建議做法（二擇一）：
  - 取代 origin：
    - `git remote set-url origin https://github.com/jimmy10800d/modern-software-dev-assignments.git`
    - `git push -u origin master`
  - 或保留原 origin，新增自己的 remote：
    - `git remote add mygit https://github.com/jimmy10800d/modern-software-dev-assignments.git`
    - `git push -u mygit master`

> 當下 workspace 是乾淨的（無 pending changes）且與遠端同步，因此沒有額外 push 內容。

---

## 2) VS Code PowerShell 找不到 conda（CommandNotFound）

### 現象
- 在某些終端（例如 cmd / Anaconda Prompt）`conda --version` 正常
- 但在 VS Code 的 PowerShell：
  - `conda : 無法辨識 'conda' 詞彙...`

### 根因
- VS Code PowerShell 沒有載入 conda 的 PowerShell hook（或被執行政策擋住）

### 解法（實際採用）
1) 確認 conda 安裝路徑：
   - `where conda`
   - 得到：`C:\Users\yehji\anaconda3\condabin\conda.bat`
   - 因此 `<CONDA_ROOT> = C:\Users\yehji\anaconda3`

2) PowerShell 執行政策阻擋 `.ps1`（UnauthorizedAccess）
   - 錯誤：`因為這個系統上已停用指令碼執行，所以無法載入 conda-hook.ps1`

3) 設定為只影響「目前使用者」的 RemoteSigned：
   - `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force`

4) 手動載入 conda PowerShell hook 並驗證：
   - `& "C:\Users\yehji\anaconda3\shell\condabin\conda-hook.ps1"`
   - `conda activate base`
   - `conda --version`  → 成功

---

## 3) 建立課程環境（Conda + Poetry）

### 建立 conda env
- `conda create -n cs146s python=3.12 -y`
- `conda activate cs146s`
- `python --version` → `Python 3.12.12`

### 安裝 Poetry
- 先嘗試：`conda install -c conda-forge poetry -y`
  - 遇到 repodata 解算時間過久/中斷
- 改用 pip（實際採用）：
  - `python -m pip install poetry`
  - `poetry --version` → `Poetry 2.2.1`

### 安裝 repo 依賴
- 在 repo root：
  - `poetry install --no-interaction`

---

## 4) week1 中文註解（導讀）

### 目的
- 不改動程式行為，只補「繁中導讀/註解」，讓日後學習時更好理解。

### 修改檔案
- `week1/assignment.md`
- `week1/k_shot_prompting.py`
- `week1/chain_of_thought.py`
- `week1/self_consistency_prompting.py`
- `week1/rag.py`
- `week1/reflexion.py`
- `week1/tool_calling.py`

### 驗證
- `python -m py_compile` 對 week1 腳本做語法檢查（避免註解造成語法錯誤）

---

## 5) 修復 pytest 在 repo root 的收集錯誤（week4~week7）

### 原始錯誤摘要
- week4/week5：`ModuleNotFoundError: No module named 'backend'`
- week6/week7：`RuntimeError: Directory 'frontend' does not exist`（import 時就掛）

### 根因 1：跨週資料夾的 import path
- 在 repo root 跑 `pytest` 時，`import backend...` 無法知道要導向哪一週的 `backend/`

### 修復 1：在各週 conftest 設定 sys.path + 清理舊 backend 模組
修改：
- `week4/backend/tests/conftest.py`
- `week5/backend/tests/conftest.py`
- `week6/backend/tests/conftest.py`
- `week7/backend/tests/conftest.py`

做法：
- 把 `weekX/` 加到 `sys.path`，確保 `import backend...` 從該週資料夾解析
- 清掉 `sys.modules` 中已載入的 `backend.*`，避免 pytest 先載入別週後造成污染

### 根因 2：frontend/data 使用相對路徑依賴 cwd
- FastAPI `StaticFiles(directory="frontend")` 以目前工作目錄為基準
- 從 repo root 跑測試時，該目錄不存在 → import-time crash

### 修復 2：用 main.py 的位置推導 week 目錄（不依賴 cwd）
修改：
- `week4/backend/app/main.py`
- `week5/backend/app/main.py`
- `week6/backend/app/main.py`
- `week7/backend/app/main.py`

做法：
- `_WEEK_DIR = Path(__file__).resolve().parents[2]`
- `_FRONTEND_DIR = _WEEK_DIR / "frontend"`
- `_DATA_DIR = _WEEK_DIR / "data"`
- 只有在 `_FRONTEND_DIR.exists()` 時才 mount static（避免 import-time crash）

### 根因 3：多週測試檔案同名造成 import mismatch
- 例如 `week4/backend/tests/test_notes.py` 與 `week5/backend/tests/test_notes.py` 同名
- pytest 預設 import 機制會發生：`import file mismatch`

### 修復 3：新增 pytest.ini 使用 importlib mode
新增：
- `pytest.ini`

內容：
- `addopts = --import-mode=importlib`

### 根因 4（Windows）：SQLite temp file 無法刪除（WinError 32）
- teardown `os.unlink(db_path)` 時，SQLAlchemy/SQLite 仍持有檔案鎖

### 修復 4：teardown 時先 dispose engine
修改：
- `week4/backend/tests/conftest.py`
- `week5/backend/tests/conftest.py`
- `week6/backend/tests/conftest.py`
- `week7/backend/tests/conftest.py`

做法：
- `finally:` 內執行：
  - `app.dependency_overrides.clear()`
  - `engine.dispose()`
  - `os.unlink(db_path)`

### 結果驗證
- 在 repo root 執行：`poetry run pytest -q`
- 結果：`13 passed`（僅剩 warnings，不影響測試通過）

---

## 後續建議
- 若只想跑某一週測試，建議在該週 backend 目錄下跑，例如：
  - `cd week4/backend; poetry run pytest -q`
- week1 主要任務是填 `TODO` 的 prompts；其他檔案（模型、溫度）盡量不要改，方便對照學習。
