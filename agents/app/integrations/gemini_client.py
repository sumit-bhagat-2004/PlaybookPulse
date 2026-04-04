"""Google Gemini API client using google-genai package"""
from google import genai
from google.genai import types
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import IntegrationException, RateLimitException


class GeminiClient:
    """Client for interacting with Google's Gemini API"""
    
    def __init__(self):
        if not settings.gemini_api_key:
            raise IntegrationException("Gemini API key not configured")
        
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model
        self.max_tokens = settings.gemini_max_tokens  # Use Gemini-specific setting
        self.temperature = settings.anthropic_temperature  # Reuse temp setting
    
    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        reraise=True
    )
    async def create_message(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Create a message using Gemini API with retry logic
        
        Args:
            prompt: User prompt
            system: System prompt (optional)
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Response text from Gemini
        """
        try:
            logger.info(f"Calling Gemini API with model: {self.model}")
            
            # Build config
            config = types.GenerateContentConfig(
                max_output_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
            )
            
            # Add system instruction if provided
            if system:
                config.system_instruction = system
            
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            
            # Extract text from response
            result = response.text
            
            logger.info(f"Gemini API call successful, response length: {len(result)}")
            return result
            
        except Exception as e:
            error_str = str(e).lower()
            if "rate" in error_str or "quota" in error_str:
                logger.error(f"Rate limit exceeded: {e}")
                raise RateLimitException(f"Gemini API rate limit exceeded: {e}")
            elif "api key" in error_str or "authentication" in error_str:
                logger.error(f"Authentication failed: {e}")
                raise IntegrationException(f"Gemini API authentication failed: {e}")
            else:
                logger.error(f"Gemini API call failed: {e}")
                raise IntegrationException(f"Gemini API error: {e}")
    
    async def analyze_with_structured_output(
        self,
        prompt: str,
        system: Optional[str] = None,
        expected_format: str = "json",
        max_retries: int = 2,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get structured output from Gemini with retry logic
        
        Args:
            prompt: User prompt
            system: System prompt
            expected_format: Expected format (json, xml, etc.)
            max_retries: Number of retry attempts for invalid responses
            max_tokens: Override max tokens (uses 8192 by default for structured output)
            
        Returns:
            Parsed structured output
        """
        import json
        
        # Use higher token limit for structured output to avoid truncation
        structured_max_tokens = max_tokens or 8192
        
        for attempt in range(max_retries):
            structured_prompt = f"{prompt}\n\nIMPORTANT: Respond with ONLY valid {expected_format} format, no explanation or markdown."
            
            response = await self.create_message(
                structured_prompt, 
                system=system,
                max_tokens=structured_max_tokens
            )
            
            if expected_format == "json":
                try:
                    # Try to extract JSON from markdown code blocks
                    json_str = self._extract_json(response)
                    return json.loads(json_str)
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse failed (attempt {attempt + 1}/{max_retries}): {e}")
                    
                    if attempt < max_retries - 1:
                        # Retry with clarification
                        prompt = f"{prompt}\n\nPrevious response was invalid JSON. Please respond with ONLY valid JSON, no markdown formatting."
                        continue
                    else:
                        # Final fallback: return minimal valid structure
                        logger.error(f"All JSON parse attempts failed. Response preview: {response[:200]}")
                        return {"error": "Failed to parse LLM response", "raw_response": response[:500]}
        
        return {"error": "Max retries exceeded", "raw_response": response[:500] if response else ""}
    
    def _extract_json(self, response: str) -> str:
        """Extract JSON from markdown code blocks or raw text"""
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        return response.strip()


# Global client instance
_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create global Gemini client"""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
