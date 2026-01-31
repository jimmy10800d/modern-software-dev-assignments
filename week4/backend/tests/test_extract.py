from backend.app.services.extract import extract_action_items  # 匯入抽取函式


def test_extract_action_items():  # 測試抽取行動項目
    text = """  # 測試文字
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()  # 去除前後空白
    items = extract_action_items(text)  # 執行抽取
    assert "TODO: write tests" in items  # 應包含 TODO
    assert "Ship it!" in items  # 應包含驚嘆號
