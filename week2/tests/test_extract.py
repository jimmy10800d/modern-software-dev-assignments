import os  # 作業系統模組
import pytest  # 測試框架

from ..app.services.extract import extract_action_items  # 匯入抽取函式


def test_extract_bullets_and_checkboxes():  # 測試子彈與勾選框抽取
    text = """  # 測試文字
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()  # 去除前後空白

    items = extract_action_items(text)  # 執行抽取
    assert "Set up database" in items  # 應包含第一項
    assert "implement API extract endpoint" in items  # 應包含第二項
    assert "Write tests" in items  # 應包含第三項
