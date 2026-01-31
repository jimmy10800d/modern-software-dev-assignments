def extract_action_items(text: str) -> list[str]:  # 從文字中抽取行動項目
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]  # 逐行清理
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]  # 依規則過濾
