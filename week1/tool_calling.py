"""Week 1 — Tool calling（工具呼叫 / function calling）"""  # 模組說明：工具呼叫

"""中文導讀："""  # 中文導讀標題
"""- 目標：讓模型輸出「一個 JSON 物件」來描述要呼叫的工具（tool name + args），而不是直接回答。"""  # 目標說明
"""- 這個檔案會："""  # 程式流程說明
"""    1) 讓模型產生 tool call JSON"""  # 步驟 1
"""    2) 解析 JSON"""  # 步驟 2
"""    3) 在本機執行對應的 Python function（TOOL_REGISTRY）"""  # 步驟 3
"""    4) 比對執行結果是否等於 expected"""  # 步驟 4
"""- 你要改的地方：只要填 `YOUR_SYSTEM_PROMPT`，讓模型穩定輸出合法 JSON。"""  # 需修改之處
"""- 怎麼跑：`poetry run python week1/tool_calling.py`"""  # 執行方式
"""重點：模型輸出必須是「純 JSON」，不要加多餘文字；否則 `json.loads` 會解析失敗。"""  # 重點提醒

# 匯入 ast 模組
import ast
# 匯入 json 模組
import json
# 匯入 os 模組
import os
# 匯入型別註解
from typing import Any, Dict, List, Optional, Tuple, Callable

# 匯入 dotenv 的 load_dotenv
from dotenv import load_dotenv
# 匯入 ollama 的 chat
from ollama import chat

# 載入環境變數
load_dotenv()

# 設定測試次數
NUM_RUNS_TIMES = 3

# ==========================
# Tool implementation (the "executor")
# ==========================
# 中文：下面這些函式是“真的會被執行”的工具；模型只負責輸出 JSON 指令，執行由本程式完成。
# 將註解節點轉為字串
def _annotation_to_str(annotation: Optional[ast.AST]) -> str:
    # 若沒有註解
    if annotation is None:
        # 回傳 None 字串
        return "None"
    # 嘗試使用 ast.unparse
    try:
        return ast.unparse(annotation)  # type: ignore[attr-defined]
    # 若解析失敗
    except Exception:
        # 若是名稱節點
        if isinstance(annotation, ast.Name):
            return annotation.id
        # 其他型別回傳型別名稱
        return type(annotation).__name__

# 讀取檔案並取得所有函式回傳型別
def _list_function_return_types(file_path: str) -> List[Tuple[str, str]]:
    # 讀檔
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    # 解析 AST
    tree = ast.parse(source)
    # 建立結果清單
    results: List[Tuple[str, str]] = []
    # 走訪最上層節點
    for node in tree.body:
        # 只處理函式定義
        if isinstance(node, ast.FunctionDef):
            # 取得回傳型別字串
            return_str = _annotation_to_str(node.returns)
            # 加入結果
            results.append((node.name, return_str))
    # Sort for stable output
    results.sort(key=lambda x: x[0])
    # 回傳結果
    return results

# 工具函式：輸出所有函式與回傳型別
def output_every_func_return_type(file_path: str = None) -> str:
    """Tool: Return a newline-delimited list of "name: return_type" for each top-level function."""
    # 若未提供檔案路徑，使用本檔案
    path = file_path or __file__
    # 若不是絕對路徑
    if not os.path.isabs(path):
        # Try file relative to this script if not absolute
        candidate = os.path.join(os.path.dirname(__file__), path)
        # 若候選檔存在
        if os.path.exists(candidate):
            path = candidate
    # 取得回傳型別清單
    pairs = _list_function_return_types(path)
    # 轉成字串
    return "\n".join(f"{name}: {ret}" for name, ret in pairs)

# Sample functions to ensure there is something to analyze
# 範例函式：加法
def add(a: int, b: int) -> int:
    return a + b

# 範例函式：問候
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Tool registry for dynamic execution by name
TOOL_REGISTRY: Dict[str, Callable[..., str]] = {
    "output_every_func_return_type": output_every_func_return_type,
}

# ==========================
# Prompt scaffolding
# ==========================

# 中文：你要讓模型輸出格式像這樣（範例）：
# {
#   "tool": "output_every_func_return_type",
#   "args": {"file_path": "tool_calling.py"}
# }

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = (
    "You are a tool-calling generator. Respond with ONLY one JSON object and no other text. "
    "The JSON must have keys 'tool' and 'args'. Use tool 'output_every_func_return_type' and args "
    "{'file_path': 'tool_calling.py'}. Do NOT add code fences, explanations, or extra fields."
)

# 解析相對路徑為可用路徑
def resolve_path(p: str) -> str:
    # 若已是絕對路徑
    if os.path.isabs(p):
        return p
    # 以本檔案所在目錄為基準
    here = os.path.dirname(__file__)
    # 組合候選路徑
    c1 = os.path.join(here, p)
    # 若存在就回傳
    if os.path.exists(c1):
        return c1
    # Try sibling of project root if needed
    return p

# 從模型輸出解析出 JSON 物件
def extract_tool_call(text: str) -> Dict[str, Any]:
    """Parse a single JSON object from the model output."""
    # 去除前後空白
    text = text.strip()
    # Some models wrap JSON in code fences; attempt to strip
    if text.startswith("```") and text.endswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json\n"):
            text = text[5:]
    # 中文：最後一定要是單一 JSON 物件字串，否則 json.loads 會丟 JSONDecodeError。
    try:
        obj = json.loads(text)
        return obj
    except json.JSONDecodeError:
        raise ValueError("Model did not return valid JSON for the tool call")

# 呼叫模型產生工具 JSON
def run_model_for_tool_call(system_prompt: str) -> Dict[str, Any]:
    response = chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Call the tool now."},
        ],
        options={"temperature": 0.3},
    )
    content = response.message.content
    return extract_tool_call(content)

# 執行工具呼叫
def execute_tool_call(call: Dict[str, Any]) -> str:
    # 取得工具名稱
    name = call.get("tool")
    # 若名稱不是字串
    if not isinstance(name, str):
        raise ValueError("Tool call JSON missing 'tool' string")
    # 取得工具函式
    func = TOOL_REGISTRY.get(name)
    # 若不存在
    if func is None:
        raise ValueError(f"Unknown tool: {name}")
    # 取得參數
    args = call.get("args", {})
    # 若參數不是 dict
    if not isinstance(args, dict):
        raise ValueError("Tool call JSON 'args' must be an object")

    # Best-effort path resolution if a file_path arg is present
    if "file_path" in args and isinstance(args["file_path"], str):
        args["file_path"] = resolve_path(args["file_path"]) if str(args["file_path"]) != "" else __file__
    elif "file_path" not in args:
        # Provide default for tools expecting file_path
        args["file_path"] = __file__

    # 執行工具函式
    return func(**args)

# 計算預期輸出
def compute_expected_output() -> str:
    # Ground-truth expected output based on the actual file contents
    return output_every_func_return_type(__file__)

# 測試提示是否成功
def test_your_prompt(system_prompt: str) -> bool:
    """Run once: require the model to produce a valid tool call; compare tool output to expected."""
    # 取得預期結果
    expected = compute_expected_output()
    # 重跑多次
    for _ in range(NUM_RUNS_TIMES):
        try:
            # 取得模型輸出的工具呼叫
            call = run_model_for_tool_call(system_prompt)
        except Exception as exc:
            print(f"Failed to parse tool call: {exc}")
            continue
        # 印出工具呼叫
        print(call)
        try:
            # 執行工具
            actual = execute_tool_call(call)
        except Exception as exc:
            print(f"Tool execution failed: {exc}")
            continue
        # 比對輸出
        if actual.strip() == expected.strip():
            print(f"Generated tool call: {call}")
            print(f"Generated output: {actual}")
            print("SUCCESS")
            return True
        else:
            print("Expected output:\n" + expected)
            print("Actual output:\n" + actual)
    return False

# 主程式入口
if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
