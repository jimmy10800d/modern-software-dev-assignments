"""Week 1 — K-shot prompting（K-shot 提示）"""  # 模組說明：K-shot 提示練習

"""中文導讀："""  # 中文導讀標題
"""- 目標：只透過「系統提示詞（system prompt）」讓模型穩定完成指定任務。"""  # 說明目標
"""- 你要改的地方：把下方 `YOUR_SYSTEM_PROMPT` 填好（通常會放 few-shot 範例與格式約束）。"""  # 說明需要修改的地方
"""- 建議做法：在 system prompt 裡明確規定「只能輸出答案本身、不要多餘文字」。"""  # 提示寫法建議
"""- 怎麼跑：在專案根目錄執行 `poetry run python week1/k_shot_prompting.py`。"""  # 執行方式
"""評分方式（此檔）：模型輸出必須只包含反轉後的字串，且完全符合 EXPECTED_OUTPUT。"""  # 評分方式

<<<<<<< HEAD
# 匯入 os 模組
import os
# 匯入 dotenv 的 load_dotenv
=======
>>>>>>> 96a9c83a959e1c030db4429856095dba89481345
from dotenv import load_dotenv
# 匯入 ollama 的 chat
from ollama import chat

# 載入環境變數
load_dotenv()

# 設定最大測試次數
NUM_RUNS_TIMES = 5

# 中文：本作業通常只需要你修改 system prompt（不要隨便調 model/temperature）。

<<<<<<< HEAD
# TODO: Fill this in!（填入你的 system prompt）
YOUR_SYSTEM_PROMPT = ""

# 使用者提示：反轉字串
USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:
=======
# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """You are a deterministic string transformer.

Task:
- Read the user's message.
- Find the LAST non-empty line.
- Reverse that line CHARACTER-BY-CHARACTER (do not split into words).
>>>>>>> 96a9c83a959e1c030db4429856095dba89481345

Output rules (strict):
- Output ONLY the reversed string.
- No extra words, no punctuation, no quotes, no explanations.
- Preserve characters exactly (case, digits, punctuation). Do not add/remove characters.

Examples:
Input:
abc
Output:
cba

Input:
httpstatus
Output:
sutatsptth

Input:
A1-b_
Output:
_b-1A
"""

<<<<<<< HEAD
# 期望輸出
=======
USER_PROMPT = "the following is a few-shot example to illustrate the task:\n\nReverse the order of letters in the following word. Only output the reversed word, no other text:\n\nhttpstatus"



>>>>>>> 96a9c83a959e1c030db4429856095dba89481345
EXPECTED_OUTPUT = "sutatsptth"

# 中文：會重跑多次，只要任一次輸出完全吻合就算成功。

# 測試函式：多次呼叫模型，任何一次命中就成功
def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    # 逐次測試
    for idx in range(NUM_RUNS_TIMES):
        # 印出當前測試次數
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        # 呼叫模型
        response = chat(
            # 指定模型
            model="mistral-nemo:12b",
            # 組合訊息（system + user）
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            # 設定溫度
            options={"temperature": 0.5},
        )
        # 取得模型輸出並去除前後空白
        output_text = response.message.content.strip()
        # 比對輸出是否符合預期
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            # 成功訊息
            print("SUCCESS")
            # 回傳成功
            return True
        else:
            # 印出預期輸出
            print(f"Expected output: {EXPECTED_OUTPUT}")
            # 印出實際輸出
            print(f"Actual output: {output_text}")
    # 全部失敗則回傳 False
    return False

# 主程式入口
if __name__ == "__main__":
    # 執行測試
    test_your_prompt(YOUR_SYSTEM_PROMPT)