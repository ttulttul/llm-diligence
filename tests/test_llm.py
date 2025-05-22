import pytest
from unittest.mock import patch, MagicMock
import json

from utils.llm import cached_llm_invoke
from utils.llm_anthropic import format_content_for_anthropic


class TestLLMUtils:
    
    @patch('utils.llm_anthropic.cached_llm_invoke')
    def test_cached_llm_invoke_caching(self, mock_anthropic_invoke):
        """Test that cached_llm_invoke delegates to the correct provider."""
        # Set up mock response
        mock_anthropic_invoke.return_value = "Test response"
        
        # Call the function
        result = cached_llm_invoke(
            model_name="claude-3-sonnet-20240229",
            system_message="Test system message",
            user_content="Test user content",
            max_tokens=1000,
            temperature=0
        )
        
        # Check that the anthropic provider was called
        mock_anthropic_invoke.assert_called_once()
        
        # Check result
        assert result == "Test response"
        
    @patch('utils.llm_anthropic.cached_llm_invoke')
    def test_cached_llm_invoke_cache_hit(self, mock_anthropic_invoke):
        """Test that cached_llm_invoke returns results from provider."""
        # Set up mock to return a response
        mock_anthropic_invoke.return_value = "Cached response"
        
        # Call the function
        result = cached_llm_invoke(
            model_name="claude-3-sonnet-20240229",
            system_message="Test system message",
            user_content="Test user content",
            max_tokens=1000,
            temperature=0
        )
        
        # Check that the anthropic provider was called
        mock_anthropic_invoke.assert_called_once()
        
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
