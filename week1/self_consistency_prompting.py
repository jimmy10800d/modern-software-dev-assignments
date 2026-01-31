"""Week 1 — Self-consistency prompting（自洽性／多次抽樣投票）"""  # 模組說明

"""中文導讀："""  # 中文導讀標題
"""- 目標：利用較高溫度讓模型產生多個不同推理路徑，最後用「多數決」提升正確率。"""  # 目標說明
"""- 你要改的地方：只要把 `YOUR_SYSTEM_PROMPT` 填好，讓每次輸出都遵守固定格式：最後一行 `Answer: <number>`。"""  # 需修改之處
"""- 這個檔案會把每次的最終答案抽出來，再用 Counter 做 majority vote。"""  # 流程說明
"""- 怎麼跑：`poetry run python week1/self_consistency_prompting.py`"""  # 執行方式

# 匯入 os 模組
import os
# 匯入正則表達式
import re
# 匯入 Counter
from collections import Counter
# 匯入 dotenv
from dotenv import load_dotenv
# 匯入 ollama 的 chat
from ollama import chat

# 載入環境變數
load_dotenv()

# 設定測試次數
NUM_RUNS_TIMES = 5

# 中文：system prompt 會影響「輸出格式是否穩定」；格式不穩定會導致抽答案失敗或投票偏移。

# TODO: Fill this in! Try to get as close to 100% correctness across all runs as possible.
YOUR_SYSTEM_PROMPT = ""

# 使用者提示
USER_PROMPT = """
Solve this problem, then give the final answer on the last line as "Answer: <number>".

Henry made two stops during his 60-mile bike trip. He first stopped after 20
miles. His second stop was 15 miles before the end of the trip. How many miles
did he travel between his first and second stops?
"""

# 預期輸出
EXPECTED_OUTPUT = "Answer: 25"

# 抽取最終答案
def extract_final_answer(text: str) -> str:
    """Extract the final 'Answer: ...' line from a verbose reasoning trace.

    - Finds the LAST line that starts with 'Answer:' (case-insensitive)
    - Normalizes to 'Answer: <number>' when a number is present
    - Falls back to returning the matched content if no number is detected
    """
    # 找出所有 Answer 行
    matches = re.findall(r"(?mi)^\s*answer\s*:\s*(.+)\s*$", text)
    # 若有匹配
    if matches:
        # 取最後一筆
        value = matches[-1].strip()
        # 嘗試抽取數字
        num_match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        # 若找到數字
        if num_match:
            return f"Answer: {num_match.group(0)}"
        # 否則回傳原內容
        return f"Answer: {value}"
    # 若沒有匹配就回傳全文
    return text.strip()

# 測試提示
def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt NUM_RUNS_TIMES, majority-vote on the extracted 'Answer: ...' lines.

    Prints "SUCCESS" if the majority answer equals EXPECTED_OUTPUT.
    """
    # 中文：answers 會收集每次抽到的 Answer: ...，最後選最多票的。
    answers: list[str] = []
    # 逐次測試
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        # 呼叫模型
        response = chat(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 1},
        )
        # 取得輸出
        output_text = response.message.content
        # 抽取最終答案
        final_answer = extract_final_answer(output_text)
        # 印出本次答案
        print(f"Run {idx + 1} answer: {final_answer}")
        # 加入答案列表
        answers.append(final_answer.strip())

    # 若沒有答案
    if not answers:
        print("No answers produced.")
        return False

    # 多數決統計
    counts = Counter(answers)
    # 取得最多票
    majority_answer, majority_count = counts.most_common(1)[0]
    # 印出多數答案
    print(f"Majority answer: {majority_answer} ({majority_count}/{len(answers)})")

    # 若多數答案符合
    if majority_answer.strip() == EXPECTED_OUTPUT.strip():
        print("SUCCESS")
        return True

    # Print distribution for debugging when majority does not match expected
    print(f"Expected output: {EXPECTED_OUTPUT}")
    print("Answer distribution:")
    for answer, count in counts.most_common():
        print(f"  {answer}: {count}")
    return False

# 主程式入口
if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)


