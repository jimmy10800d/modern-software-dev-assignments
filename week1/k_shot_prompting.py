"""Week 1 — K-shot prompting（K-shot 提示）

中文導讀：
- 目標：只透過「系統提示詞（system prompt）」讓模型穩定完成指定任務。
- 你要改的地方：把下方 `YOUR_SYSTEM_PROMPT` 填好（通常會放 few-shot 範例與格式約束）。
- 建議做法：在 system prompt 裡明確規定「只能輸出答案本身、不要多餘文字」。
- 怎麼跑：在專案根目錄執行 `poetry run python week1/k_shot_prompting.py`。

評分方式（此檔）：模型輸出必須只包含反轉後的字串，且完全符合 EXPECTED_OUTPUT。
"""

from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# 中文：本作業通常只需要你修改 system prompt（不要隨便調 model/temperature）。

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """You are a deterministic string transformer.

Task:
- Read the user's message.
- Find the LAST non-empty line.
- Reverse that line CHARACTER-BY-CHARACTER (do not split into words).

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

USER_PROMPT = "the following is a few-shot example to illustrate the task:\n\nReverse the order of letters in the following word. Only output the reversed word, no other text:\n\nhttpstatus"



EXPECTED_OUTPUT = "sutatsptth"


# 中文：會重跑多次，只要任一次輸出完全吻合就算成功。

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.5},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)