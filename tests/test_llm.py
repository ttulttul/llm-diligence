import pytest
from unittest.mock import patch, MagicMock
import json

from utils.llm import cached_llm_invoke, format_content_for_anthropic


class TestLLMUtils:
    
    @patch('utils.llm.cache')
    @patch('utils.llm.anthropic.Anthropic')
    def test_cached_llm_invoke_caching(self, mock_anthropic, mock_cache):
        """Test that cached_llm_invoke uses the cache correctly."""
        # Set up mock cache behavior
        mock_cache.get.return_value = None
        mock_anthropic_instance = MagicMock()
        mock_anthropic.return_value = mock_anthropic_instance
        mock_anthropic_instance.messages.create.return_value = MagicMock(content=[{"text": "Test response"}])
        
        # Call the function
        result = cached_llm_invoke(
            model_name="claude-3-sonnet-20240229",
            system_message="Test system message",
            user_content="Test user content",
            max_tokens=1000,
            temperature=0
        )
        
        # Check that cache was checked
        mock_cache.get.assert_called_once()
        
        # Check that anthropic was called
        mock_anthropic_instance.messages.create.assert_called_once()
        
        # Check that result was cached
        mock_cache.set.assert_called_once()
        
        # Check result
        assert result == "Test response"
        
    @patch('utils.llm.cache')
    @patch('utils.llm.anthropic.Anthropic')
    def test_cached_llm_invoke_cache_hit(self, mock_anthropic, mock_cache):
        """Test that cached_llm_invoke returns cached results when available."""
        # Set up mock cache to return a cached result
        mock_cache.get.return_value = "Cached response"
        
        # Call the function
        result = cached_llm_invoke(
            model_name="claude-3-sonnet-20240229",
            system_message="Test system message",
            user_content="Test user content",
            max_tokens=1000,
            temperature=0
        )
        
        # Check that cache was checked
        mock_cache.get.assert_called_once()
        
        # Check that anthropic was not called
        mock_anthropic.assert_not_called()
        
        # Check result is from cache
        assert result == "Cached response"
    
    def test_format_content_for_anthropic(self):
        """Test that content is formatted correctly for Anthropic."""
        # Test with a string
        content = "Test content"
        result = format_content_for_anthropic(content)
        assert result == [{"type": "text", "text": "Test content"}]
        
        # Test with a list of strings
        content = ["Part 1", "Part 2"]
        result = format_content_for_anthropic(content)
        assert result == [{"type": "text", "text": "Part 1\nPart 2"}]
        
        # Test with a PDF path
        with patch('utils.llm.extract_text_from_pdf', return_value="PDF content"):
            content = "path/to/document.pdf"
            result = format_content_for_anthropic(content)
            assert result == [{"type": "text", "text": "PDF content"}]
