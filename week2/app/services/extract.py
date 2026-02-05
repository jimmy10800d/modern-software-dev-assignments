from __future__ import annotations  # 延後型別評估

import os  # 作業系統功能
import re  # 正則表達式
from typing import List  # 型別註解
import json  # JSON 模組
from typing import Any  # Any 型別
from ollama import chat  # Ollama 模型呼叫
from dotenv import load_dotenv  # 載入環境變數

load_dotenv()  # 讀取 .env

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")  # 子彈符號或編號前綴
KEYWORD_PREFIXES = (  # 關鍵字前綴
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:  # 判斷該行是否像行動項目
    stripped = line.strip().lower()  # 去空白並轉小寫
    if not stripped:  # 空行則不是行動項目
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):  # 符合符號或編號
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):  # 符合關鍵字前綴
        return True
    if "[ ]" in stripped or "[todo]" in stripped:  # 符合勾選框格式
        return True
    return False  # 其他情況為否


def extract_action_items(text: str) -> List[str]:  # 從文字中抽取行動項目
    lines = text.splitlines()  # 逐行拆分
    extracted: List[str] = []  # 收集結果
    for raw_line in lines:  # 逐行處理
        line = raw_line.strip()  # 去除空白
        if not line:  # 空行略過
            continue
        if _is_action_line(line):  # 若為行動項目
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)  # 去除前綴
            cleaned = cleaned.strip()  # 再次去空白
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()  # 移除空方框
            cleaned = cleaned.removeprefix("[todo]").strip()  # 移除 [todo]
            extracted.append(cleaned)  # 加入結果
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:  # 若沒有抽到
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())  # 依句號切句
        for sentence in sentences:  # 逐句處理
            s = sentence.strip()  # 去空白
            if not s:  # 空句略過
                continue
            if _looks_imperative(s):  # 判斷是否祈使句
                extracted.append(s)  # 加入結果
    # Deduplicate while preserving order
    seen: set[str] = set()  # 用於去重
    unique: List[str] = []  # 去重後結果
    for item in extracted:  # 逐項處理
        lowered = item.lower()  # 轉小寫
        if lowered in seen:  # 若已存在
            continue
        seen.add(lowered)  # 記錄已見
        unique.append(item)  # 加入結果
    return unique  # 回傳去重後清單


def _looks_imperative(sentence: str) -> bool:  # 判斷是否祈使句
    words = re.findall(r"[A-Za-z']+", sentence)  # 抽取英文字
    if not words:  # 無單字則否
        return False
    first = words[0]  # 取第一個字
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {  # 常見祈使動詞
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters  # 判斷是否命中


# ============================================================================
# TODO 1: LLM-powered action item extraction
# ============================================================================

def extract_action_items_llm(
    text: str,
    model: str = "llama3.1:8b",
) -> List[str]:
    """
    使用 LLM（透過 Ollama）從文字中抽取行動項目。
    
    Args:
        text: 輸入的筆記文字
        model: Ollama 模型名稱，預設為 llama3.1:8b
        
    Returns:
        行動項目的字串清單
    """
    # 若輸入為空或只有空白，直接回傳空清單
    if not text or not text.strip():
        return []
    
    # 系統提示詞：指導 LLM 如何抽取行動項目
    system_prompt = """You are an action item extractor. 
Your task is to extract actionable tasks from the user's note.

Rules:
1. Return ONLY a valid JSON array of strings.
2. Each string should be a single action item.
3. Do not include any explanation or additional text.
4. If there are no action items, return an empty array: []
5. Keep action items concise and actionable.

Example input:
"Meeting notes: We need to fix the login bug. Also, update the documentation and schedule a review meeting."

Example output:
["Fix the login bug", "Update the documentation", "Schedule a review meeting"]
"""

    try:
        # 呼叫 Ollama 模型
        response = chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract action items from this note:\n\n{text}"},
            ],
            format="json",  # 要求 JSON 格式輸出
            options={"temperature": 0.1},  # 低溫度確保穩定輸出
        )
        
        # 取得回應內容
        content = response.message.content.strip()
        
        # 解析 JSON
        result = json.loads(content)
        
        # 確保結果是陣列
        if isinstance(result, list):
            # 確保每個元素都是字串
            return [str(item).strip() for item in result if item]
        elif isinstance(result, dict):
            # 有時 LLM 會回傳 {"action_items": [...]} 格式
            for key in ["action_items", "items", "tasks", "actions"]:
                if key in result and isinstance(result[key], list):
                    return [str(item).strip() for item in result[key] if item]
        
        # 若格式不符，回傳空清單
        return []
        
    except json.JSONDecodeError:
        # JSON 解析失敗，嘗試用 regex 抽取
        # 尋找類似 ["item1", "item2"] 的模式
        match = re.search(r'\[.*?\]', content, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
                if isinstance(result, list):
                    return [str(item).strip() for item in result if item]
            except json.JSONDecodeError:
                pass
        return []
        
    except Exception as e:
        # 其他錯誤，印出警告並回傳空清單
        print(f"Warning: LLM extraction failed: {e}")
        return []
