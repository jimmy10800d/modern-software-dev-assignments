"""Week 1 — Chain-of-thought（思維鏈）"""  # 模組說明：思維鏈提示

"""中文導讀："""  # 中文導讀標題
"""- 目標：讓模型在解題時「先推理、再輸出最後答案」，並且最後一行固定格式：`Answer: <number>`。"""  # 目標描述
"""- 你要改的地方：只要把 `YOUR_SYSTEM_PROMPT` 填好。"""  # 需要修改的欄位
"""- 小技巧：在 system prompt 強制輸出格式、要求最後一行一定要有 Answer，並提醒不要漏掉。"""  # 提示寫法建議
"""- 怎麼跑：`poetry run python week1/chain_of_thought.py`"""  # 執行方式
"""注意：這個測試只抓最後一行的 Answer，不會檢查你中間推理寫了什麼。"""  # 測試說明

# 匯入 os 模組
import os
# 匯入正則表達式模組
import re
# 匯入 dotenv 的 load_dotenv
from dotenv import load_dotenv
# 匯入 ollama 的 chat
from ollama import chat

# 載入環境變數
load_dotenv()

# 設定最大測試次數
NUM_RUNS_TIMES = 5

# 中文：你只需要填 system prompt；題目在 USER_PROMPT。

# TODO: Fill this in!（填入你的 system prompt）
YOUR_SYSTEM_PROMPT = ""

# 使用者提示：數學題
USER_PROMPT = """
Solve this problem, then give the final answer on the last line as "Answer: <number>".

what is 3^{12345} (mod 100)?
"""

# 預期輸出
EXPECTED_OUTPUT = "Answer: 43"

# 抽取最終答案的函式
def extract_final_answer(text: str) -> str:
    """Extract the final 'Answer: ...' line from a verbose reasoning trace.

    - Finds the LAST line that starts with 'Answer:' (case-insensitive)
    - Normalizes to 'Answer: <number>' when a number is present
    - Falls back to returning the matched content if no number is detected
    """
    # 找出所有以 Answer: 開頭的行
    matches = re.findall(r"(?mi)^\s*answer\s*:\s*(.+)\s*$", text)
    # 若有符合項目
    if matches:
        # 取最後一筆
        value = matches[-1].strip()
        # 嘗試抽取數字
        num_match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        # 若找到數字，標準化輸出
        if num_match:
            return f"Answer: {num_match.group(0)}"
        # 若無數字，回傳原內容
        return f"Answer: {value}"
    # 若沒找到 Answer 行，回傳全文
    return text.strip()

# 中文：測試會跑多次，任何一次命中 EXPECTED_OUTPUT 就算成功。

# 測試函式：多次呼叫模型
def test_your_prompt(system_prompt: str) -> bool:
    """Run up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    # 逐次測試
    for idx in range(NUM_RUNS_TIMES):
        # 印出測試次數
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        # 呼叫模型
        response = chat(
            # 指定模型
            model="llama3.1:8b",
            # 系統與使用者訊息
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            # 設定溫度
            options={"temperature": 0.3},
        )
        # 取得輸出文字
        output_text = response.message.content
        # 抽取最終答案
        final_answer = extract_final_answer(output_text)
        # 比對是否符合預期
        if final_answer.strip() == EXPECTED_OUTPUT.strip():
            # 成功訊息
            print("SUCCESS")
            # 回傳成功
            return True
        else:
            # 印出預期與實際
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {final_answer}")
    # 全部失敗回傳 False
    return False

# 主程式入口
if __name__ == "__main__":
    # 執行測試
    test_your_prompt(YOUR_SYSTEM_PROMPT)


