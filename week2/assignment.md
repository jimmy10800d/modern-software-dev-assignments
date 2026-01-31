# Week 2 – Action Item Extractor

This week, we will be expanding upon a minimal FastAPI + SQLite app that converts free‑form notes into enumerated action items.

## 中文註解（本週重點）
- 目標：擴充既有 FastAPI + SQLite 筆記→行動項目（action items）應用。
- 你要做的事：在後端加入 LLM 抽取、補測試、重構、加端點與前端按鈕、並產出 README。
- 交付：完成程式修改並在 writeup.md 記錄你用的提示與變更。

***We recommend reading this entire document before getting started.***

Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`


## Getting Started

### Cursor Set Up
Follow these instructions to set up Cursor and open your project:
1. Redeem your free year of Cursor Pro: https://cursor.com/students
2. Download Cursor: https://cursor.com/download
3. To enable the Cursor command line tool, open Cursor and press `Command (⌘) + Shift+ P` for Mac users (or `Ctrl + Shift + P` for non-Mac users) to open the Command Palette. Type: `Shell Command: Install 'cursor' command`. Select it and hit Enter.
4. Open a new terminal window, navigate to your project root, and run: `cursor .`

### Current Application
Here's how you can start running the current starter application: 
1. Activate your conda environment.
```
conda activate cs146s 
```
2. From the project root, run the server:
```
poetry run uvicorn week2.app.main:app --reload
```
3. Open a web browser and navigate to http://127.0.0.1:8000/.
4. Familiarize yourself with the current state of the application. Make sure you can successfully input notes and produce the extracted action item checklist. 

## Exercises
For each exercise, use Cursor to help you implement the specified improvements to the current action item extractor application.

As you work through the assignment, use `writeup.md` to document your progress. Be sure to include the prompts you use, as well as any changes made by you or Cursor. We will be grading based on the contents of the write-up. Please also include comments throughout your code to document your changes. 

### TODO 1: Scaffold a New Feature

Analyze the existing `extract_action_items()` function in `week2/app/services/extract.py`, which currently extracts action items using predefined heuristics.

Your task is to implement an **LLM-powered** alternative, `extract_action_items_llm()`, that utilizes Ollama to perform action item extraction via a large language model.

Some  tips:
- To produce structured outputs (i.e. JSON array of strings), refer to this documentation: https://ollama.com/blog/structured-outputs 
- To browse available Ollama models, refer to this documentation: https://ollama.com/library. Note that larger models will be more resource-intensive, so start small. To pull and run a model: `ollama run {MODEL_NAME}`

### TODO 2: Add Unit Tests 

Write unit tests for `extract_action_items_llm()` covering multiple inputs (e.g., bullet lists, keyword-prefixed lines, empty input) in `week2/tests/test_extract.py`.

### TODO 3: Refactor Existing Code for Clarity

Perform a refactor of the code in the backend, focusing in particular on well-defined API contracts/schemas, database layer cleanup, app lifecycle/configuration, error handling. 

### TODO 4: Use Agentic Mode to Automate Small Tasks

1. Integrate the LLM-powered extraction as a new endpoint. Update the frontend to include an "Extract LLM" button that, when clicked, triggers the extraction process via the new endpoint.

2. Expose one final endpoint to retrieve all notes. Update the frontend to include a "List Notes" button that, when clicked, fetches and displays them.

### TODO 5: Generate a README from the Codebase

***Learning Goal:***
*Students learn how AI can introspect a codebase and produce documentation automatically, showcasing Cursor’s ability to parse code context and translate it into human‑readable form.*

Use Cursor to analyze the current codebase and generate a well-structured `README.md` file. The README should include, at a minimum:
- A brief overview of the project
- How to set up and run the project
- API endpoints and functionality
- Instructions for running the test suite

## Deliverables
Fill out `week2/writeup.md` according to the instructions provided. Make sure all your changes are documented in your codebase. 

## Evaluation rubric (100 pts total)
- 20 points per part 1-5 (10 for the generated code and 10 for each prompt).

---

## 中文註解（詳細版）
### 本週目標
以現有 FastAPI + SQLite 應用為基礎，擴充「從自由文字筆記萃取行動項目」的功能，並練習 LLM + 測試 + 重構 + 前後端整合。

### 起始設定與啟動
1. 啟用 conda 環境：`conda activate cs146s`
2. 啟動伺服器：`poetry run uvicorn week2.app.main:app --reload`
3. 瀏覽器開啟 `http://127.0.0.1:8000/`
4. 先熟悉目前功能（輸入筆記 → 產生 checklist）

### TODO 任務說明
1) **加入 LLM 抽取**：
	- 研讀 `extract_action_items()`（啟發式抽取）。
	- 新增 `extract_action_items_llm()` 使用 Ollama 模型輸出結構化 JSON（字串陣列）。

2) **新增測試**：
	- 在 `week2/tests/test_extract.py` 補 LLM 抽取的單元測試（多種輸入型態）。

3) **重構後端**：
	- 改善 API schema/contract、資料庫層、生命週期設定、錯誤處理等。

4) **Agentic 自動化小任務**：
	- 新增 LLM 抽取端點與前端按鈕「Extract LLM」。
	- 新增「列出所有 notes」端點與前端按鈕「List Notes」。

5) **產生 README**：
	- 讓 AI 讀程式碼自動生成 README：專案概述、安裝/執行、API 端點、測試指令。

### 交付與評分
- `week2/writeup.md` 需記錄你的提示與變更。
- 每個 TODO 20 分（10 分程式 + 10 分 prompt）。