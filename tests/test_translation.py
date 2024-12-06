import pytest
import json
from unittest.mock import patch, Mock, AsyncMock
import requests

# Import the function to test
from discord_translator.translation import translate_text

# Tests specifically for the LLM translation functionality
class TestTranslation:
    @pytest.mark.asyncio
    async def test_successful_translation(self):
        """Test successful translation with valid input"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Bonjour le monde"
        }

        with patch('requests.post', return_value=mock_response):
            result = await translate_text("Hello world", "french")
            assert result == "Bonjour le monde"

    @pytest.mark.asyncio
    async def test_translation_api_error(self):
        """Test handling of API errors"""
        with patch('requests.post', side_effect=requests.exceptions.RequestException("API Error")):
            result = await translate_text("Hello world", "french")
            assert result is None

    @pytest.mark.asyncio
    async def test_translation_invalid_json(self):
        """Test handling of invalid JSON response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)

        with patch('requests.post', return_value=mock_response):
            result = await translate_text("Hello world", "french")
            assert result is None

    @pytest.mark.asyncio
    async def test_translation_missing_response_field(self):
        """Test handling of missing 'response' field in API response"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # Empty response without 'response' field

        with patch('requests.post', return_value=mock_response):
            result = await translate_text("Hello world", "french")
            assert result is None

    @pytest.mark.asyncio
    async def test_translation_timeout(self):
        """Test handling of API timeout"""
        with patch('requests.post', side_effect=requests.exceptions.Timeout("Timeout")):
            result = await translate_text("Hello world", "french")
            assert result is None

    @pytest.mark.asyncio
    async def test_translation_server_error(self):
        """Test handling of server error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Server Error")

        with patch('requests.post', return_value=mock_response):
            result = await translate_text("Hello world", "french")
            assert result is None

    @pytest.mark.asyncio
    async def test_translation_request_format(self):
        """Test that the request is formatted correctly"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test"}

        with patch('requests.post') as mock_post:
            mock_post.return_value = mock_response
            await translate_text("Hello world", "french")

            # Verify the request format
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args

            assert args[0] == 'http://localhost:11434/api/generate'
            # assert kwargs['json']['model'] == 'llama2'
            assert kwargs['json']['model'].startswith('llama')
            assert kwargs['json']['prompt'] == 'Translate the following text to french. Translation only no explanations or commentary will be accepted: "Hello world"'
            assert kwargs['json']['stream'] is False
            assert kwargs['timeout'] == 30

    @pytest.mark.asyncio
    async def test_translation_empty_input(self):
        """Test handling of empty input text"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": ""}

        with patch('requests.post', return_value=mock_response):
            result = await translate_text("", "french")
            assert result == ""

    @pytest.mark.asyncio
    async def test_translation_long_text(self):
        """Test handling of long input text"""
        long_text = "Hello world " * 100
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Long translated text"}

        with patch('requests.post', return_value=mock_response):
            result = await translate_text(long_text, "french")
            assert result == "Long translated text"


if __name__ == '__main__':
    pytest.main([__file__])