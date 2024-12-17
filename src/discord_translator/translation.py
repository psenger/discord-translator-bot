import os

from dotenv import load_dotenv
import requests
import json
from typing import Optional

# Load environment variables
load_dotenv()

async def translate_text(text: str, target_language: str) -> Optional[str]:
    """
    Translate text using Ollama API

    Args:
        text (str): Text to translate
        target_language (str): Target language for translation

    Returns:
        Optional[str]: Translated text or None if translation fails
    """

    load_dotenv()
    try:

        ollama_model = os.getenv('OLLAMA_MODEL')
        ollama_url = os.getenv('OLLAMA_URL')

        # Use aiohttp or httpx for async HTTP requests in production
        response = requests.post(
            ollama_url,
            json={
                'model': ollama_model,
                'prompt': (
                    f'Translate the following text to {target_language}. '
                    f'IMPORTANT: You must preserve ALL original formatting, including spaces, newlines, markdown, and '
                    f'alignment. Your response must contain ONLY the translation with the preserved formatting - no '
                    f'additional text, no alternatives, no explanations: '
                    f'\n\n{text}'
                ),
                'stream': False  # Ensure we get complete response
            },
            timeout=30  # Add timeout to prevent hanging
        )

        response.raise_for_status()

        data = response.json()
        print(f"Raw JSON response from API: {data}")
        if 'response' in data:
            # Clean up the response to ensure single translation
            translation = data['response'].strip()

            # Remove any "Translation:" prefix if present
            if translation.lower().startswith('translation:'):
                translation = translation.split(':', 1)[1].strip()

            # If there are multiple translations (separated by OR, or newlines), take only the first
            # translation = translation.split('\n')[0].split(' OR ')[0].split(' or ')[0].strip()

            return translation if translation else None

        return None

    except requests.exceptions.RequestException as e:
        print(f"Translation request error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error during translation: {e}")
        return None