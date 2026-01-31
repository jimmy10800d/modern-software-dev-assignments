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
