"""
Week2 TODO 1 解答：新增 LLM 抽取功能
extract_ans.py - 包含原本的啟發式抽取與新增的 LLM 抽取函式
"""
from __future__ import annotations  # 延後型別評估

import os  # 作業系統功能
import re  # 正則表達式
import json  # JSON 模組
from typing import List, Any, Optional  # 型別註解
from pydantic import BaseModel  # Pydantic 資料驗證
from dotenv import load_dotenv  # 載入環境變數

load_dotenv()  # 讀取 .env

# ============================================================
# 常數與正則表達式定義
# ============================================================

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")  # 子彈符號或編號前綴
KEYWORD_PREFIXES = (  # 關鍵字前綴
    "todo:",
    "action:",
    "next:",
)

# LLM 相關設定
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")  # 預設使用 llama3.2:1b 模型


# ============================================================
# Pydantic 結構化輸出模型（供 LLM 使用）
# ============================================================

class ActionItemsResponse(BaseModel):
    """LLM 回傳的結構化行動項目清單"""
    action_items: List[str]  # 行動項目字串陣列


# ============================================================
# 啟發式抽取函式（原有功能）
# ============================================================

def _is_action_line(line: str) -> bool:
    """判斷該行是否像行動項目
    
    Args:
        line: 單行文字
        
    Returns:
        bool: 是否為行動項目
    """
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


def _looks_imperative(sentence: str) -> bool:
    """判斷是否為祈使句
    
    Args:
        sentence: 完整句子
        
    Returns:
        bool: 是否為祈使句
    """
    words = re.findall(r"[A-Za-z']+", sentence)  # 抽取英文字
    if not words:  # 無單字則否
        return False
    first = words[0]  # 取第一個字
    # 常見祈使動詞
    imperative_starters = {
        "add", "create", "implement", "fix", "update", "write",
        "check", "verify", "refactor", "document", "design",
        "investigate", "review", "test", "deploy", "configure",
        "setup", "remove", "delete", "move", "rename", "merge",
    }
    return first.lower() in imperative_starters  # 判斷是否命中


def extract_action_items(text: str) -> List[str]:
    """從文字中抽取行動項目（啟發式方法）
    
    使用正則表達式與關鍵字比對來識別行動項目。
    
    Args:
        text: 輸入的筆記文字
        
    Returns:
        List[str]: 抽取到的行動項目清單
    """
    lines = text.splitlines()  # 逐行拆分
    extracted: List[str] = []  # 收集結果
    
    for raw_line in lines:  # 逐行處理
        line = raw_line.strip()  # 去除空白
        if not line:  # 空行略過
            continue
        if _is_action_line(line):  # 若為行動項目
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)  # 去除前綴
            cleaned = cleaned.strip()  # 再次去空白
            # 移除常見 checkbox 標記
            cleaned = cleaned.removeprefix("[ ]").strip()  # 移除空方框
            cleaned = cleaned.removeprefix("[todo]").strip()  # 移除 [todo]
            extracted.append(cleaned)  # 加入結果
    
    # Fallback: 若沒有抽到，依句號切分並挑選祈使句
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())  # 依句號切句
        for sentence in sentences:  # 逐句處理
            s = sentence.strip()  # 去空白
            if not s:  # 空句略過
                continue
            if _looks_imperative(s):  # 判斷是否祈使句
                extracted.append(s)  # 加入結果
    
    # 去重但保持順序
    seen: set[str] = set()  # 用於去重
    unique: List[str] = []  # 去重後結果
    for item in extracted:  # 逐項處理
        lowered = item.lower()  # 轉小寫
        if lowered in seen:  # 若已存在
            continue
        seen.add(lowered)  # 記錄已見
        unique.append(item)  # 加入結果
    
    return unique  # 回傳去重後清單


# ============================================================
# TODO 1: LLM 抽取函式（新增功能）
# ============================================================

def extract_action_items_llm(
    text: str,
    model: Optional[str] = None,
    timeout: float = 30.0
) -> List[str]:
    """使用 LLM（Ollama）從文字中抽取行動項目
    
    透過大型語言模型分析筆記內容，智慧識別並抽取行動項目。
    使用 Pydantic 結構化輸出確保回傳格式正確。
    
    Args:
        text: 輸入的筆記文字
        model: Ollama 模型名稱（預設使用環境變數 OLLAMA_MODEL）
        timeout: API 呼叫超時秒數
        
    Returns:
        List[str]: 抽取到的行動項目清單
        
    Raises:
        ValueError: 當輸入文字為空時
        RuntimeError: 當 LLM 呼叫失敗時
    """
    # 參數驗證
    if not text or not text.strip():  # 若輸入為空
        return []  # 回傳空清單
    
    # 使用指定模型或預設模型
    model_name = model or OLLAMA_MODEL
    
    # 構建 prompt
    system_prompt = """You are an expert at extracting actionable items from notes.
Analyze the given text and identify all action items, tasks, or to-dos.
Return ONLY a JSON object with an "action_items" field containing an array of strings.
Each action item should be a clear, concise task.
Do not include explanations, just the JSON."""

    user_prompt = f"""Extract all action items from the following notes:

{text}

Return the result as a JSON object with "action_items" array."""

    try:
        # 匯入 ollama（延遲匯入以支援測試 mock）
        from ollama import chat  # Ollama API 呼叫
        
        # 呼叫 Ollama API（使用結構化輸出）
        response = chat(
            model=model_name,  # 使用指定模型
            messages=[
                {"role": "system", "content": system_prompt},  # 系統提示
                {"role": "user", "content": user_prompt},  # 使用者輸入
            ],
            format=ActionItemsResponse.model_json_schema(),  # 結構化輸出 schema
            options={"timeout": timeout},  # 超時設定
        )
        
        # 解析回應
        content = response.message.content  # 取得回應內容
        
        # 嘗試解析 JSON
        try:
            parsed = json.loads(content)  # 解析 JSON
            
            # 驗證並提取 action_items
            if isinstance(parsed, dict) and "action_items" in parsed:
                items = parsed["action_items"]  # 取得行動項目
                if isinstance(items, list):
                    # 過濾並清理結果
                    result = [
                        str(item).strip() 
                        for item in items 
                        if item and str(item).strip()
                    ]
                    return result  # 回傳結果
            
            # 如果格式不符預期，嘗試其他解析方式
            if isinstance(parsed, list):  # 若直接是陣列
                return [str(item).strip() for item in parsed if item]
                
        except json.JSONDecodeError:
            # JSON 解析失敗，嘗試從文字中提取
            # 嘗試找到 JSON 區塊
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    if "action_items" in parsed:
                        return [str(item).strip() for item in parsed["action_items"] if item]
                except json.JSONDecodeError:
                    pass  # 仍然失敗，繼續往下
            
            # 最後嘗試：按行分割
            lines = content.strip().split('\n')
            items = []
            for line in lines:
                cleaned = line.strip().lstrip('-*•').strip()
                if cleaned and not cleaned.startswith('{') and not cleaned.startswith('['):
                    items.append(cleaned)
            if items:
                return items
        
        return []  # 無法解析則回傳空清單
        
    except ImportError:
        # ollama 未安裝
        raise RuntimeError("Ollama library not installed. Please install with: pip install ollama")
        
    except Exception as e:
        # 其他錯誤
        raise RuntimeError(f"LLM extraction failed: {str(e)}")


def extract_action_items_llm_fallback(
    text: str,
    model: Optional[str] = None,
    use_fallback: bool = True
) -> List[str]:
    """帶有 fallback 的 LLM 抽取函式
    
    先嘗試使用 LLM 抽取，若失敗則回退到啟發式方法。
    
    Args:
        text: 輸入的筆記文字
        model: Ollama 模型名稱
        use_fallback: 是否在 LLM 失敗時使用啟發式方法
        
    Returns:
        List[str]: 抽取到的行動項目清單
    """
    try:
        # 先嘗試 LLM 抽取
        items = extract_action_items_llm(text, model=model)
        if items:  # 若有結果
            return items
    except Exception as e:
        # LLM 失敗
        if not use_fallback:
            raise  # 不使用 fallback 則拋出錯誤
        print(f"LLM extraction failed, falling back to heuristic: {e}")
    
    # 回退到啟發式方法
    if use_fallback:
        return extract_action_items(text)
    
    return []  # 回傳空清單
