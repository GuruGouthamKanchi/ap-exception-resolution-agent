import os
import sys
import pytest
from dotenv import load_dotenv

# Ensure parent directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from services.gemini_client import GeminiClient

def test_gemini_client_reason():
    # Verify api key is present. If not, skip or fail clearly
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY not found in environment variables.")

    client = GeminiClient()
    try:
        response = client.reason("Reply with exactly the word OK")
        print(f"Gemini response: {response}")
        assert "OK" in response.strip()
    except Exception as e:
        if "rate limit" in str(e).lower() or "quota" in str(e).lower() or "limit" in str(e).lower():
            pytest.skip(f"Skipping Gemini integration test due to API rate limit: {str(e)}")
        raise

