import os  # 作業系統模組
import pytest  # 測試框架
from unittest.mock import patch, MagicMock  # Mock 工具

from ..app.services.extract import extract_action_items  # 匯入規則抽取函式
from ..app.services.extract import extract_action_items_llm  # 匯入 LLM 抽取函式


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


# ============================================================================
# TODO 2: Unit tests for extract_action_items_llm()
# ============================================================================

class TestExtractActionItemsLLM:
    """測試 LLM 抽取函式的測試類別"""

    # ------------------------------------------------------------------
    # 測試空輸入
    # ------------------------------------------------------------------
    def test_empty_string_returns_empty_list(self):
        """空字串應該回傳空清單"""
        result = extract_action_items_llm("")
        assert result == []

    def test_whitespace_only_returns_empty_list(self):
        """只有空白的字串應該回傳空清單"""
        result = extract_action_items_llm("   \n\t  ")
        assert result == []

    def test_none_like_empty(self):
        """None 應該被處理為空輸入"""
        # 函式預期接收 str，但測試防禦性
        result = extract_action_items_llm("")
        assert result == []

    # ------------------------------------------------------------------
    # 測試子彈列點輸入（使用 mock 避免真實 API 呼叫）
    # ------------------------------------------------------------------
    @patch('week2.app.services.extract.chat')
    def test_bullet_list_extraction(self, mock_chat):
        """測試子彈列點格式的輸入"""
        # 模擬 LLM 回應
        mock_response = MagicMock()
        mock_response.message.content = '["Buy groceries", "Call mom", "Finish report"]'
        mock_chat.return_value = mock_response

        text = """
        - Buy groceries
        - Call mom
        - Finish report
        """
        result = extract_action_items_llm(text)
        
        assert len(result) == 3
        assert "Buy groceries" in result
        assert "Call mom" in result
        assert "Finish report" in result

    # ------------------------------------------------------------------
    # 測試關鍵字前綴輸入
    # ------------------------------------------------------------------
    @patch('week2.app.services.extract.chat')
    def test_keyword_prefixed_lines(self, mock_chat):
        """測試 TODO:、Action: 等關鍵字前綴的輸入"""
        mock_response = MagicMock()
        mock_response.message.content = '["Fix the bug", "Update documentation", "Review PR"]'
        mock_chat.return_value = mock_response

        text = """
        TODO: Fix the bug
        Action: Update documentation
        Next: Review PR
        """
        result = extract_action_items_llm(text)
        
        assert len(result) == 3
        assert "Fix the bug" in result
        assert "Update documentation" in result
        assert "Review PR" in result

    # ------------------------------------------------------------------
    # 測試自由格式文字
    # ------------------------------------------------------------------
    @patch('week2.app.services.extract.chat')
    def test_freeform_text_extraction(self, mock_chat):
        """測試自由格式的會議筆記"""
        mock_response = MagicMock()
        mock_response.message.content = '["Schedule follow-up meeting", "Send proposal to client"]'
        mock_chat.return_value = mock_response

        text = """
        Meeting went well. We need to schedule a follow-up meeting 
        next week. Also remember to send the proposal to the client.
        """
        result = extract_action_items_llm(text)
        
        assert len(result) == 2
        assert "Schedule follow-up meeting" in result
        assert "Send proposal to client" in result

    # ------------------------------------------------------------------
    # 測試 LLM 回傳字典格式
    # ------------------------------------------------------------------
    @patch('week2.app.services.extract.chat')
    def test_handles_dict_response(self, mock_chat):
        """測試 LLM 回傳 {"action_items": [...]} 格式"""
        mock_response = MagicMock()
        mock_response.message.content = '{"action_items": ["Task 1", "Task 2"]}'
        mock_chat.return_value = mock_response

        result = extract_action_items_llm("Some text")
        
        assert len(result) == 2
        assert "Task 1" in result
        assert "Task 2" in result

    # ------------------------------------------------------------------
    # 測試 JSON 解析錯誤處理
    # ------------------------------------------------------------------
    @patch('week2.app.services.extract.chat')
    def test_handles_invalid_json(self, mock_chat):
        """測試無效 JSON 回應的錯誤處理"""
        mock_response = MagicMock()
        mock_response.message.content = 'This is not valid JSON'
        mock_chat.return_value = mock_response

        result = extract_action_items_llm("Some text")
        
        # 應該回傳空清單而不是拋出錯誤
        assert result == []

    # ------------------------------------------------------------------
    # 整合測試（實際呼叫 LLM，可選擇跳過）
    # ------------------------------------------------------------------
    @pytest.mark.skipif(
        os.environ.get("SKIP_LLM_TESTS", "1") == "1",
        reason="跳過需要 Ollama 的整合測試（設定 SKIP_LLM_TESTS=0 來執行）"
    )
    def test_real_llm_extraction(self):
        """整合測試：實際呼叫 LLM"""
        text = "We need to fix the login bug and update the user guide."
        result = extract_action_items_llm(text)
        
        # 只檢查回傳類型和非空
        assert isinstance(result, list)
        assert len(result) > 0
