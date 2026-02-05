"""Week 1 — Reflexion（反思式改進）"""  # 模組說明

"""中文導讀："""  # 中文導讀標題
"""- 目標：讓模型先產生一版程式碼，跑測試得到失敗原因，再把「上一版程式碼 + 失敗訊息」回饋給模型，"""  # 目標說明
"""    讓模型自我修正產生 improved code。"""  # 目標補充
"""- 你要改的地方："""  # 需修改的地方
"""    1) `YOUR_REFLEXION_PROMPT`：告訴模型如何根據失敗訊息修正，並且仍然只輸出單一 Python code block。"""  # 修改點 1
"""    2) `your_build_reflexion_context`：把 prev_code 與 failures 組成清楚的回饋內容。"""  # 修改點 2
"""- 怎麼跑：`poetry run python week1/reflexion.py`"""  # 執行方式

# 匯入 os 模組
import os
# 匯入正則表達式
import re
# 匯入型別註解
from typing import Callable, List, Tuple
# 匯入 dotenv
from dotenv import load_dotenv
# 匯入 ollama 的 chat
from ollama import chat

# 載入環境變數
load_dotenv()

# 設定測試次數
NUM_RUNS_TIMES = 1

# 中文：SYSTEM_PROMPT 固定要求模型只輸出 function code；你主要設計「反思 prompt」讓它修正錯誤。

# 系統提示：產生函式碼
SYSTEM_PROMPT = """
You are a coding assistant. Output ONLY a single fenced Python code block that defines
the function is_valid_password(password: str) -> bool. No prose or comments.
Keep the implementation minimal.
"""

# TODO: Fill this in!
YOUR_REFLEXION_PROMPT = """You are a coding assistant that fixes Python code based on test failures.

Your task:
1. Analyze the previous code and the test failure messages.
2. Fix the code to pass all tests.
3. Output ONLY a single fenced Python code block with the corrected function.
4. The function must be named is_valid_password(password: str) -> bool.
5. No prose, no explanations, no comments outside the code block.

Password validation rules (all must be satisfied):
- At least 8 characters long
- Contains at least one lowercase letter
- Contains at least one uppercase letter
- Contains at least one digit
- Contains at least one special character from: !@#$%^&*()-_
- No whitespace allowed
"""

# Ground-truth test suite used to evaluate generated code
SPECIALS = set("!@#$%^&*()-_")
TEST_CASES: List[Tuple[str, bool]] = [
    ("Password1!", True),       # valid
    ("password1!", False),      # missing uppercase
    ("Password!", False),       # missing digit
    ("Password1", False),       # missing special
]

# 抽取程式碼區塊
def extract_code_block(text: str) -> str:
    # 嘗試抽取 python code block
    m = re.findall(r"```python\n([\s\S]*?)```", text, flags=re.IGNORECASE)
    if m:
        return m[-1].strip()
    # 嘗試抽取一般 code block
    m = re.findall(r"```\n([\s\S]*?)```", text)
    if m:
        return m[-1].strip()
    return text.strip()

# 從字串載入函式
def load_function_from_code(code_str: str) -> Callable[[str], bool]:
    # 建立命名空間
    namespace: dict = {}
    # 執行程式碼
    exec(code_str, namespace)  # noqa: S102 (executing controlled code from model for exercise)
    # 取得函式
    func = namespace.get("is_valid_password")
    # 若不可呼叫就拋錯
    if not callable(func):
        raise ValueError("No callable is_valid_password found in generated code")
    return func

# 評估函式是否通過測試
def evaluate_function(func: Callable[[str], bool]) -> Tuple[bool, List[str]]:
    # 收集失敗訊息
    failures: List[str] = []
    # 逐一測試
    for pw, expected in TEST_CASES:
        try:
            # 執行函式
            result = bool(func(pw))
        except Exception as exc:
            failures.append(f"Input: {pw} → raised exception: {exc}")
            continue

        # 若結果不符預期
        if result != expected:
            # Compute diagnostic based on ground-truth rules
            reasons = []
            if len(pw) < 8:
                reasons.append("length < 8")
            if not any(c.islower() for c in pw):
                reasons.append("missing lowercase")
            if not any(c.isupper() for c in pw):
                reasons.append("missing uppercase")
            if not any(c.isdigit() for c in pw):
                reasons.append("missing digit")
            if not any(c in SPECIALS for c in pw):
                reasons.append("missing special")
            if any(c.isspace() for c in pw):
                reasons.append("has whitespace")

            failures.append(
                f"Input: {pw} → expected {expected}, got {result}. Failing checks: {', '.join(reasons) or 'unknown'}"
            )

    return (len(failures) == 0, failures)

# 中文：第一次先生成初版程式，若測試失敗就進入 reflexion（單次迭代）。

# 產生初版函式
def generate_initial_function(system_prompt: str) -> str:
    response = chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Provide the implementation now."},
        ],
        options={"temperature": 0.2},
    )
    return extract_code_block(response.message.content)

# 建立反思上下文
def your_build_reflexion_context(prev_code: str, failures: List[str]) -> str:
    """TODO: Build the user message for the reflexion step using prev_code and failures.

    Return a string that will be sent as the user content alongside the reflexion system prompt.
    """
    failures_text = "\n".join(f"- {f}" for f in failures)
    return f"""Here is the previous code that failed some tests:

```python
{prev_code}
```

Test failures:
{failures_text}

Please fix the code to pass all tests. Output only the corrected Python code block."""

# 執行反思
def apply_reflexion(
    reflexion_prompt: str,
    build_context: Callable[[str, List[str]], str],
    prev_code: str,
    failures: List[str],
) -> str:
    # 建立反思上下文
    reflection_context = build_context(prev_code, failures)
    # 印出反思內容
    print(f"REFLECTION CONTEXT: {reflection_context}, {reflexion_prompt}")
    # 呼叫模型修正
    response = chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": reflexion_prompt},
            {"role": "user", "content": reflection_context},
        ],
        options={"temperature": 0.2},
    )
    return extract_code_block(response.message.content)

# 執行完整反思流程
def run_reflexion_flow(
    system_prompt: str,
    reflexion_prompt: str,
    build_context: Callable[[str, List[str]], str],
) -> bool:
    # 1) Generate initial function
    initial_code = generate_initial_function(system_prompt)
    print("Initial code:\n" + initial_code)
    func = load_function_from_code(initial_code)
    passed, failures = evaluate_function(func)
    if passed:
        print("SUCCESS (initial implementation passed all tests)")
        return True
    else:
        print(f"FAILURE (initial implementation failed some tests): {failures}")

    # 2) Single reflexion iteration
    improved_code = apply_reflexion(reflexion_prompt, build_context, initial_code, failures)
    print("\nImproved code:\n" + improved_code)
    improved_func = load_function_from_code(improved_code)
    passed2, failures2 = evaluate_function(improved_func)
    if passed2:
        print("SUCCESS")
        return True

    print("Tests still failing after reflexion:")
    for f in failures2:
        print("- " + f)
    return False

# 主程式入口
if __name__ == "__main__":
    run_reflexion_flow(SYSTEM_PROMPT, YOUR_REFLEXION_PROMPT, your_build_reflexion_context)
