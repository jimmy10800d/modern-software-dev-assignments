# Week 2 - Action Item Extractor

> 一個將自由格式筆記轉換為可執行待辦事項的 FastAPI + SQLite 應用程式。

## 專案概述

Action Item Extractor 是一個網頁應用程式，可以從使用者輸入的筆記中自動抽取行動項目（Action Items）。支援兩種抽取方式：

1. **規則式抽取**：使用正則表達式和啟發式規則識別待辦事項
2. **LLM 抽取**：使用大型語言模型（透過 Ollama）智慧抽取待辦事項

## 功能特色

- ✅ 從筆記中自動抽取待辦事項
- ✅ 支援規則式和 LLM 兩種抽取模式
- ✅ 儲存筆記和待辦事項到 SQLite 資料庫
- ✅ 標記待辦事項完成狀態
- ✅ 列出所有儲存的筆記
- ✅ 簡潔的網頁前端介面

## 安裝與設定

### 前置需求

- Python 3.10+
- [Poetry](https://python-poetry.org/) 套件管理器
- [Ollama](https://ollama.com/) 本地 LLM 執行環境（用於 LLM 抽取功能）

### 安裝步驟

1. **啟用 conda 環境**
   ```bash
   conda activate cs146s
   ```

2. **安裝依賴套件**
   ```bash
   poetry install
   ```

3. **下載 Ollama 模型**（用於 LLM 抽取功能）
   ```bash
   ollama pull llama3.1:8b
   ```

## 啟動應用程式

從專案根目錄執行：

```bash
poetry run uvicorn week2.app.main:app --reload
```

然後在瀏覽器開啟 http://127.0.0.1:8000/

## API 端點

### Notes（筆記）

| 方法 | 端點 | 說明 |
|------|------|------|
| `GET` | `/notes` | 列出所有筆記 |
| `POST` | `/notes` | 建立新筆記 |
| `GET` | `/notes/{note_id}` | 取得單一筆記 |

### Action Items（行動項目）

| 方法 | 端點 | 說明 |
|------|------|------|
| `POST` | `/action-items/extract` | 使用規則式方法抽取行動項目 |
| `POST` | `/action-items/extract-llm` | 使用 LLM 抽取行動項目 |
| `GET` | `/action-items` | 列出所有行動項目 |
| `POST` | `/action-items/{id}/done` | 標記行動項目完成狀態 |

### 請求/回應範例

**抽取行動項目（規則式）**
```bash
curl -X POST http://127.0.0.1:8000/action-items/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "- Buy groceries\n- Call mom", "save_note": true}'
```

**抽取行動項目（LLM）**
```bash
curl -X POST http://127.0.0.1:8000/action-items/extract-llm \
  -H "Content-Type: application/json" \
  -d '{"text": "Meeting notes: We need to fix the bug and update docs.", "save_note": true}'
```

**列出所有筆記**
```bash
curl http://127.0.0.1:8000/notes
```

## 執行測試

```bash
# 執行所有測試
poetry run pytest week2/tests/ -v

# 只執行抽取功能測試
poetry run pytest week2/tests/test_extract.py -v

# 執行整合測試（需要 Ollama）
SKIP_LLM_TESTS=0 poetry run pytest week2/tests/test_extract.py -v
```

## 專案結構

```
week2/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 應用程式入口
│   ├── db.py                # SQLite 資料庫操作
│   ├── schemas.py           # Pydantic 請求/回應模型
│   ├── routers/
│   │   ├── action_items.py  # 行動項目 API 路由
│   │   └── notes.py         # 筆記 API 路由
│   └── services/
│       └── extract.py       # 抽取服務（規則式 + LLM）
├── frontend/
│   └── index.html           # 前端網頁
├── tests/
│   └── test_extract.py      # 單元測試
├── data/
│   └── app.db               # SQLite 資料庫檔案
├── assignment.md            # 作業說明
├── writeup.md               # 作業記錄
└── README.md                # 本文件
```

## 技術棧

- **後端框架**: FastAPI
- **資料庫**: SQLite
- **資料驗證**: Pydantic
- **LLM 執行**: Ollama
- **測試框架**: pytest

## 授權

本專案為 Stanford CS146 課程作業。
