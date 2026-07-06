import os
import time
import json
import logging
from google import genai
from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class GeminiExtractionError(Exception):
    """Raised when structured extraction or reasoning fails due to API errors or bad output format."""
    pass

class GeminiClient:
    """
    The single point of contact with Google Gemini.
    
    All agents should use this class rather than initializing or calling the SDK directly.
    Provides logic for structured Pydantic extraction, free-form reasoning, error handling,
    and automatic transient error retries.
    """
    def __init__(self):
        # The genai.Client automatically reads GEMINI_API_KEY from environment variables
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY environment variable is not set. API calls may fail.")
        
        # Initialize client. If api_key is None, it defaults to the environment variable.
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"


    def _call_with_retry(self, func, *args, **kwargs):
        """Helper to invoke a function with exponential backoff retry."""
        attempt = 0
        generic_retries = 2
        rate_limit_retries = 3
        
        generic_delay = 1.0
        rate_limit_delay = 20.0
        
        generic_attempt = 0
        rate_limit_attempt = 0
        
        while True:
            try:
                return func(*args, **kwargs)
            except APIError as e:
                err_msg = (e.message or "").lower()
                is_rate_limit = e.code == 429 or "quota" in err_msg or "rate limit" in err_msg
                
                if is_rate_limit:
                    if rate_limit_attempt < rate_limit_retries:
                        rate_limit_attempt += 1
                        logger.warning(
                            f"Rate limit hit, waiting {rate_limit_delay}s before retry "
                            f"(attempt {rate_limit_attempt}/{rate_limit_retries})"
                        )
                        time.sleep(rate_limit_delay)
                        rate_limit_delay *= 2
                    else:
                        raise GeminiExtractionError(f"Gemini API call failed (Rate Limit Exceeded): {e.message} (Code: {e.code})") from e
                else:
                    is_transient = e.code in [500, 502, 503, 504]
                    if is_transient and generic_attempt < generic_retries:
                        generic_attempt += 1
                        logger.warning(
                            f"Transient Gemini API error ({e.code}). Retrying in {generic_delay}s "
                            f"(Attempt {generic_attempt}/{generic_retries})..."
                        )
                        time.sleep(generic_delay)
                        generic_delay *= 2
                    else:
                        raise GeminiExtractionError(f"Gemini API call failed: {e.message} (Code: {e.code})") from e
            except Exception as e:
                raise GeminiExtractionError(f"Unexpected error calling Gemini API: {str(e)}") from e


    def extract_structured(self, prompt: str, response_schema: type) -> dict:
        """
        Call Gemini to generate structured output conforming to the response_schema Pydantic model.
        
        Args:
            prompt (str): Prompt to send to the model.
            response_schema (type): Pydantic BaseModel class for validation.
            
        Returns:
            dict: The validated model instance as a dictionary.
        """
        def _execute():
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.1
            )
            return self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

        response = self._call_with_retry(_execute)
        text = response.text
        if not text:
            raise GeminiExtractionError("Gemini returned an empty response.")
        
        try:
            # Parse and validate using the Pydantic schema
            parsed_data = json.loads(text)
            if issubclass(response_schema, BaseModel):
                validated_model = response_schema.model_validate(parsed_data)
                return validated_model.model_dump()
            return parsed_data
        except (json.JSONDecodeError, ValueError) as e:
            raise GeminiExtractionError(f"Failed to parse or validate JSON output from Gemini: {str(e)}. Raw text: {text}") from e

    def reason(self, prompt: str) -> str:
        """
        Call Gemini for free-form reasoning or text generation.
        
        Args:
            prompt (str): Prompt to send to the model.
            
        Returns:
            str: The raw generated text response.
        """
        def _execute():
            return self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

        response = self._call_with_retry(_execute)
        if not response.text:
            raise GeminiExtractionError("Gemini returned an empty text response.")
        return response.text
