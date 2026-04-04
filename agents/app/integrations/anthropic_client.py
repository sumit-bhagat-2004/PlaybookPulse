"""Anthropic Claude API client"""
import anthropic
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import IntegrationException, RateLimitException


class AnthropicClient:
    """Client for interacting with Anthropic's Claude API"""
    
    def __init__(self):
        if not settings.anthropic_api_key:
            raise IntegrationException("Anthropic API key not configured")
        
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
        self.max_tokens = settings.anthropic_max_tokens
        self.temperature = settings.anthropic_temperature
    
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
        Create a message using Claude API with retry logic
        
        Args:
            prompt: User prompt
            system: System prompt (optional)
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Response text from Claude
        """
        try:
            logger.info(f"Calling Claude API with model: {self.model}")
            
            message_params = {
                "model": self.model,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            if system:
                message_params["system"] = system
            
            response = await self.client.messages.create(**message_params)
            
            # Extract text from response
            result = response.content[0].text
            
            logger.info(f"Claude API call successful, response length: {len(result)}")
            return result
            
        except anthropic.RateLimitError as e:
            logger.error(f"Rate limit exceeded: {e}")
            raise RateLimitException(f"Claude API rate limit exceeded: {e}")
        except anthropic.AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise IntegrationException(f"Claude API authentication failed: {e}")
        except Exception as e:
            logger.error(f"Claude API call failed: {e}")
            raise IntegrationException(f"Claude API error: {e}")
    
    async def create_message_stream(
        self,
        prompt: str,
        system: Optional[str] = None
    ):
        """
        Stream responses from Claude API
        
        Args:
            prompt: User prompt
            system: System prompt (optional)
            
        Yields:
            Chunks of response text
        """
        try:
            message_params = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": [{"role": "user", "content": prompt}],
                "stream": True
            }
            
            if system:
                message_params["system"] = system
            
            async with self.client.messages.stream(**message_params) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            logger.error(f"Claude API stream failed: {e}")
            raise IntegrationException(f"Claude API stream error: {e}")
    
    async def analyze_with_structured_output(
        self,
        prompt: str,
        system: Optional[str] = None,
        expected_format: str = "json",
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Get structured output from Claude with retry logic
        
        Args:
            prompt: User prompt
            system: System prompt
            expected_format: Expected format (json, xml, etc.)
            max_retries: Number of retry attempts for invalid responses
            
        Returns:
            Parsed structured output
        """
        import json
        
        for attempt in range(max_retries):
            structured_prompt = f"{prompt}\n\nIMPORTANT: Respond with ONLY valid {expected_format} format, no explanation."
            
            response = await self.create_message(structured_prompt, system=system)
            
            if expected_format == "json":
                try:
                    # Try to extract JSON from markdown code blocks
                    json_str = self._extract_json(response)
                    return json.loads(json_str)
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse failed (attempt {attempt + 1}/{max_retries}): {e}")
                    
                    if attempt < max_retries - 1:
                        # Retry with clarification
                        prompt = f"{prompt}\n\nPrevious response was invalid JSON. Please respond with ONLY valid JSON."
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
_client: Optional[AnthropicClient] = None


def get_anthropic_client() -> AnthropicClient:
    """Get or create global Anthropic client"""
    global _client
    if _client is None:
        _client = AnthropicClient()
    return _client
