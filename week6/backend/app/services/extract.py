def extract_action_items(text: str) -> list[str]:  # 從文字中抽取行動項目
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]  # 逐行清理
    results: list[str] = []  # 結果清單
    for line in lines:  # 逐行處理
        normalized = line.lower()  # 轉小寫
        if normalized.startswith("todo:") or normalized.startswith("action:"):  # 判斷前綴
            results.append(line)  # 加入結果
        elif line.endswith("!"):  # 驚嘆號結尾
            results.append(line)  # 加入結果
    return results  # 回傳結果


API_TOKEN = "sk_live_51HACKED_EXAMPLE_DO_NOT_USE_abcdefghijklmnopqrstuvwxyz"  # 範例 API Token（示範用）

