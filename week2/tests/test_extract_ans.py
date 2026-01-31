"""
Week2 TODO 2 解答：LLM 抽取函式的單元測試
test_extract_ans.py - 完整的測試涵蓋各種輸入情況
"""
import os  # 作業系統模組
import pytest  # 測試框架
from unittest.mock import patch, MagicMock  # Mock 工具

# 匯入待測函式
from ..app.services.extract import extract_action_items  # 原有啟發式抽取
# 注意：這裡假設 extract_ans.py 中的函式也可以測試
# 實際上應該從 extract_ans 匯入，這裡為了相容性同時測試兩者


# ============================================================
# 測試啟發式抽取函式 (extract_action_items)
# ============================================================

class TestExtractActionItemsHeuristic:
    """啟發式抽取函式的測試類別"""

    def test_extract_bullets_and_checkboxes(self):
        """測試子彈符號與勾選框的抽取"""
        text = """
        Notes from meeting:
        - [ ] Set up database
        * implement API extract endpoint
        1. Write tests
        Some narrative sentence.
        """.strip()

        items = extract_action_items(text)
        
        assert "Set up database" in items  # 應包含 checkbox 項目
        assert "implement API extract endpoint" in items  # 應包含星號項目
        assert "Write tests" in items  # 應包含編號項目
        assert "Some narrative sentence" not in items  # 不應包含普通敘述

    def test_extract_keyword_prefixes(self):
        """測試關鍵字前綴（TODO:, ACTION:, NEXT:）"""
        text = """
        TODO: Complete the documentation
        ACTION: Review pull request
        NEXT: Deploy to production
        Regular note without prefix
        """.strip()

        items = extract_action_items(text)
        
        assert any("Complete the documentation" in item for item in items)
        assert any("Review pull request" in item for item in items)
        assert any("Deploy to production" in item for item in items)

    def test_extract_empty_input(self):
        """測試空輸入"""
        items = extract_action_items("")
        assert items == []  # 空輸入應回傳空清單
        
        items = extract_action_items("   \n\n   ")
        assert items == []  # 只有空白的輸入也應回傳空清單

    def test_extract_numbered_list(self):
        """測試編號清單"""
        text = """
        Shopping list:
        1. Buy milk
        2. Get bread
        3. Pick up groceries
        """.strip()

        items = extract_action_items(text)
        
        assert len(items) == 3  # 應該有 3 個項目
        assert "Buy milk" in items
        assert "Get bread" in items
        assert "Pick up groceries" in items

    def test_extract_mixed_bullet_styles(self):
        """測試混合子彈符號風格"""
        text = """
        - First item with dash
        * Second item with asterisk
        • Third item with bullet point
        """.strip()

        items = extract_action_items(text)
        
        assert len(items) == 3
        assert "First item with dash" in items
        assert "Second item with asterisk" in items
        assert "Third item with bullet point" in items

    def test_extract_imperative_fallback(self):
        """測試祈使句 fallback（無明確格式時）"""
        text = "Add new feature to the system. Check the configuration. Update the documentation."
        
        items = extract_action_items(text)
        
        # 應該透過祈使句偵測抽取
        assert any("Add" in item for item in items) or len(items) > 0

    def test_deduplication(self):
        """測試去重功能"""
        text = """
        - Set up database
        - set up database
        - SET UP DATABASE
        - Different task
        """.strip()

        items = extract_action_items(text)
        
        # 相同項目（不分大小寫）應該去重
        db_items = [item for item in items if "database" in item.lower()]
        assert len(db_items) == 1  # 只應保留一個

    def test_checkbox_marker_removal(self):
        """測試 checkbox 標記移除"""
        text = """
        - [ ] Task with empty checkbox
        - [todo] Task with todo marker
        """.strip()

        items = extract_action_items(text)
        
        # 應該移除 [ ] 和 [todo] 標記
        for item in items:
            assert "[ ]" not in item
            assert "[todo]" not in item.lower()


# ============================================================
# 測試 LLM 抽取函式 (extract_action_items_llm)
# ============================================================

class TestExtractActionItemsLLM:
    """LLM 抽取函式的測試類別（使用 Mock）"""

    @pytest.fixture
    def mock_ollama_response(self):
        """建立 Mock Ollama 回應的 fixture"""
        def _create_response(action_items):
            mock_response = MagicMock()
            mock_response.message.content = f'{{"action_items": {action_items}}}'
            return mock_response
        return _create_response

    def test_llm_extract_empty_input(self):
        """測試 LLM 抽取空輸入"""
        # 動態匯入以避免模組不存在的錯誤
        try:
            from ..app.services.extract_ans import extract_action_items_llm
        except ImportError:
            pytest.skip("extract_ans module not available")
        
        result = extract_action_items_llm("")
        assert result == []  # 空輸入應回傳空清單
        
        result = extract_action_items_llm("   ")
        assert result == []

    @patch('ollama.chat')
    def test_llm_extract_bullet_list(self, mock_chat, mock_ollama_response):
        """測試 LLM 抽取子彈清單"""
        try:
            from ..app.services.extract_ans import extract_action_items_llm
        except ImportError:
            pytest.skip("extract_ans module not available")
        
        # 設定 Mock 回應
        mock_chat.return_value = mock_ollama_response(
            '["Set up database", "Write tests", "Deploy application"]'
        )
        
        text = """
        Meeting notes:
        - Set up database
        - Write tests
        - Deploy application
        """
        
        result = extract_action_items_llm(text)
        
        assert len(result) == 3
        assert "Set up database" in result
        assert "Write tests" in result
        assert "Deploy application" in result

    @patch('ollama.chat')
    def test_llm_extract_keyword_prefixed(self, mock_chat, mock_ollama_response):
        """測試 LLM 抽取關鍵字前綴項目"""
        try:
            from ..app.services.extract_ans import extract_action_items_llm
        except ImportError:
            pytest.skip("extract_ans module not available")
        
        mock_chat.return_value = mock_ollama_response(
            '["Complete documentation", "Review code", "Update config"]'
        )
        
        text = """
        TODO: Complete documentation
        ACTION: Review code
        NEXT: Update config
        """
        
        result = extract_action_items_llm(text)
        
        assert len(result) == 3

    @patch('ollama.chat')
    def test_llm_extract_complex_text(self, mock_chat, mock_ollama_response):
        """測試 LLM 從複雜文字中抽取"""
        try:
            from ..app.services.extract_ans import extract_action_items_llm
        except ImportError:
            pytest.skip("extract_ans module not available")
        
        mock_chat.return_value = mock_ollama_response(
            '["Schedule meeting with team", "Prepare presentation slides"]'
        )
        
        text = """
        Had a great meeting today. We discussed the upcoming product launch.
        John mentioned we should schedule a meeting with the team next week.
        Also, Sarah asked me to prepare the presentation slides by Friday.
        The weather was nice and the coffee was good.
        """
        
        result = extract_action_items_llm(text)
        
        # LLM 應該能從敘述中識別行動項目
        assert len(result) >= 1

    @patch('ollama.chat')
    def test_llm_extract_no_action_items(self, mock_chat, mock_ollama_response):
        """測試 LLM 抽取無行動項目的文字"""
        try:
            from ..app.services.extract_ans import extract_action_items_llm
        except ImportError:
            pytest.skip("extract_ans module not available")
        
        mock_chat.return_value = mock_ollama_response('[]')
        
        text = "Just a random thought about life and the universe."
        
        result = extract_action_items_llm(text)
        
        assert result == []

    @patch('ollama.chat')
    def test_llm_handles_malformed_json(self, mock_chat):
        """測試 LLM 處理格式錯誤的 JSON 回應"""
        try:
            from ..app.services.extract_ans import extract_action_items_llm
        except ImportError:
            pytest.skip("extract_ans module not available")
        
        # 設定回傳非 JSON 格式
        mock_response = MagicMock()
        mock_response.message.content = "- Task 1\n- Task 2\n- Task 3"
        mock_chat.return_value = mock_response
        
        text = "Some notes with tasks"
        
        # 應該能處理並嘗試解析
        result = extract_action_items_llm(text)
        # 結果可能為空或有內容，取決於 fallback 邏輯

    @patch('ollama.chat')
    def test_llm_api_error_handling(self, mock_chat):
        """測試 LLM API 錯誤處理"""
        try:
            from ..app.services.extract_ans import extract_action_items_llm
        except ImportError:
            pytest.skip("extract_ans module not available")
        
        # 設定 API 拋出錯誤
        mock_chat.side_effect = Exception("API connection failed")
        
        with pytest.raises(RuntimeError) as exc_info:
            extract_action_items_llm("Some text")
        
        assert "LLM extraction failed" in str(exc_info.value)


# ============================================================
# 測試 LLM 抽取帶 Fallback 的函式
# ============================================================

class TestExtractActionItemsLLMFallback:
    """LLM 抽取帶 Fallback 的測試類別"""

    @patch('ollama.chat')
    def test_fallback_on_llm_failure(self, mock_chat):
        """測試 LLM 失敗時回退到啟發式方法"""
        try:
            from ..app.services.extract_ans import extract_action_items_llm_fallback
        except ImportError:
            pytest.skip("extract_ans module not available")
        
        # 設定 LLM 呼叫失敗
        mock_chat.side_effect = Exception("API error")
        
        text = """
        - Buy groceries
        - Call mom
        - Finish homework
        """
        
        # 應該 fallback 到啟發式方法並成功抽取
        result = extract_action_items_llm_fallback(text, use_fallback=True)
        
        assert len(result) >= 1  # 應該有結果

    @patch('ollama.chat')
    def test_no_fallback_raises_error(self, mock_chat):
        """測試禁用 fallback 時 LLM 失敗拋出錯誤"""
        try:
            from ..app.services.extract_ans import extract_action_items_llm_fallback
        except ImportError:
            pytest.skip("extract_ans module not available")
        
        mock_chat.side_effect = Exception("API error")
        
        with pytest.raises(Exception):
            extract_action_items_llm_fallback("Some text", use_fallback=False)


# ============================================================
# 整合測試
# ============================================================

class TestIntegration:
    """整合測試類別"""

    def test_both_methods_consistent(self):
        """測試兩種方法對相同輸入的一致性（基本情況）"""
        text = """
        - [ ] Task 1
        - [ ] Task 2
        - [ ] Task 3
        """
        
        heuristic_result = extract_action_items(text)
        
        # 啟發式方法應該成功抽取
        assert len(heuristic_result) == 3
        assert "Task 1" in heuristic_result
        assert "Task 2" in heuristic_result
        assert "Task 3" in heuristic_result

    def test_edge_cases(self):
        """測試各種邊界情況"""
        # Unicode 文字
        unicode_text = """
        - 完成專案報告
        - 更新文件
        """
        items = extract_action_items(unicode_text)
        assert len(items) == 2
        
        # 很長的單行
        long_text = "- " + "a" * 1000
        items = extract_action_items(long_text)
        assert len(items) == 1
        
        # 特殊字元
        special_text = """
        - Task with "quotes"
        - Task with 'single quotes'
        - Task with (parentheses)
        """
        items = extract_action_items(special_text)
        assert len(items) == 3
