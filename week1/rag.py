"""Week 1 — RAG（Retrieval-Augmented Generation，檢索增強生成）"""  # 模組說明

"""中文導讀："""  # 中文導讀標題
"""- 目標：模型只能使用你提供的「Context」來回答；Context 來自本機的文件（這裡是簡化 API docs）。"""  # 目標說明
"""- 你要改的地方："""  # 需修改的地方
"""    1) `YOUR_SYSTEM_PROMPT`：約束模型只能用 Context、輸出必須是單一 Python code block。"""  # 修改點 1
"""    2) `YOUR_CONTEXT_PROVIDER`：從 CORPUS 挑出「真的相關」的文件片段（或全部提供）。"""  # 修改點 2
"""- 測試方式：不比對整段文字，而是檢查生成 code 是否包含 REQUIRED_SNIPPETS。"""  # 測試說明
"""- 怎麼跑：`poetry run python week1/rag.py`"""  # 執行方式

# 匯入 os 模組
import os
# 匯入正則表達式
import re
# 匯入型別註解
from typing import List, Callable
# 匯入 dotenv
from dotenv import load_dotenv
# 匯入 ollama 的 chat
from ollama import chat

# 載入環境變數
load_dotenv()

# 設定測試次數
NUM_RUNS_TIMES = 5

# 定義資料檔案路徑
DATA_FILES: List[str] = [
    os.path.join(os.path.dirname(__file__), "data", "api_docs.txt"),
]

# 中文：這裡會嘗試讀 week1/data/api_docs.txt 當作知識庫；不存在時會在 CORPUS 中標記 missing。

# 載入語料庫
def load_corpus_from_files(paths: List[str]) -> List[str]:
    # 初始化語料
    corpus: List[str] = []
    # 逐一讀檔
    for p in paths:
        # 若檔案存在
        if os.path.exists(p):
            try:
                # 讀檔內容
                with open(p, "r", encoding="utf-8") as f:
                    corpus.append(f.read())
            except Exception as exc:
                # 讀取失敗記錄
                corpus.append(f"[load_error] {p}: {exc}")
        else:
            # 檔案缺失記錄
            corpus.append(f"[missing_file] {p}")
    # 回傳語料
    return corpus

# Load corpus from external files (simple API docs). If missing, fall back to inline snippet
CORPUS: List[str] = load_corpus_from_files(DATA_FILES)

# 問題內容
QUESTION = (
    "Write a Python function `fetch_user_name(user_id: str, api_key: str) -> str` that calls the documented API "
    "to fetch a user by id and returns only the user's name as a string."
)

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = ""

# For this simple example
# For this coding task, validate by required snippets rather than exact string
REQUIRED_SNIPPETS = [
    "def fetch_user_name(",
    "requests.get",
    "/users/",
    "X-API-Key",
    "return",
]

# 內容提供者：挑選相關上下文
def YOUR_CONTEXT_PROVIDER(corpus: List[str]) -> List[str]:
    """TODO: Select and return the relevant subset of documents from CORPUS for this task.

    For example, return [] to simulate missing context, or [corpus[0]] to include the API docs.
    """
    # 中文：最簡單就是 `return [corpus[0]]`；進階可以做關鍵字搜尋/切段，只回傳需要的部分。
    return []

# 建立 user prompt
def make_user_prompt(question: str, context_docs: List[str]) -> str:
    # 若有 context
    if context_docs:
        context_block = "\n".join(f"- {d}" for d in context_docs)
    else:
        context_block = "(no context provided)"
    # 組合提示
    return (
        f"Context (use ONLY this information):\n{context_block}\n\n"
        f"Task: {question}\n\n"
        "Requirements:\n"
        "- Use the documented Base URL and endpoint.\n"
        "- Send the documented authentication header.\n"
        "- Raise for non-200 responses.\n"
        "- Return only the user's name string.\n\n"
        "Output: A single fenced Python code block with the function and necessary imports.\n"
    )

# 中文：為了穩定抓 code，測試會抽取「最後一段」```python ...``` code block。

# 抽取程式碼區塊
def extract_code_block(text: str) -> str:
    """Extract the last fenced Python code block, or any fenced code block, else return text."""
    # Try ```python ... ``` first
    m = re.findall(r"```python\n([\s\S]*?)```", text, flags=re.IGNORECASE)
    if m:
        return m[-1].strip()
    # Fallback to any fenced code block
    m = re.findall(r"```\n([\s\S]*?)```", text)
    if m:
        return m[-1].strip()
    return text.strip()

# 測試提示
def test_your_prompt(system_prompt: str, context_provider: Callable[[List[str]], List[str]]) -> bool:
    """Run up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT."""
    # 取得 context
    context_docs = context_provider(CORPUS)
    # 建立 user prompt
    user_prompt = make_user_prompt(QUESTION, context_docs)

    # 逐次測試
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        # 呼叫模型
        response = chat(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            options={"temperature": 0.0},
        )
        # 取得輸出
        output_text = response.message.content
        # 抽取程式碼
        code = extract_code_block(output_text)
        # 檢查必要片段
        missing = [s for s in REQUIRED_SNIPPETS if s not in code]
        if not missing:
            print(output_text)
            print("SUCCESS")
            return True
        else:
            print("Missing required snippets:")
            for s in missing:
                print(f"  - {s}")
            print("Generated code:\n" + code)
    return False

# 主程式入口
if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT, YOUR_CONTEXT_PROVIDER)
