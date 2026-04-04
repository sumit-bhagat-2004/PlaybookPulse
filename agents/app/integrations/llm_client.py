"""Unified LLM Client - Factory for different LLM providers"""
from typing import Dict, Any, Optional

from app.config import settings
from app.utils.logger import logger
from app.utils.exceptions import IntegrationException


class LLMClient:
    """Unified client that delegates to the configured LLM provider"""
    
    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client based on configuration"""
        if self.provider == "gemini":
            if not settings.gemini_api_key:
                raise IntegrationException(
                    "GEMINI_API_KEY is required when LLM_PROVIDER=gemini. "
                    "Get your key from https://aistudio.google.com/apikey"
                )
            from app.integrations.gemini_client import GeminiClient
            self._client = GeminiClient()
            logger.info("Using Gemini LLM provider")
            
        elif self.provider == "anthropic":
            if not settings.anthropic_api_key:
                raise IntegrationException(
                    "ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic. "
                    "Get your key from https://console.anthropic.com/"
                )
            from app.integrations.anthropic_client import AnthropicClient
            self._client = AnthropicClient()
            logger.info("Using Anthropic LLM provider")
            
        else:
            raise IntegrationException(
                f"Unknown LLM provider: {self.provider}. "
                f"Supported providers: gemini, anthropic"
            )
    
    async def create_message(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Create a message using the configured LLM provider"""
        return await self._client.create_message(
            prompt=prompt,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    async def analyze_with_structured_output(
        self,
        prompt: str,
        system: Optional[str] = None,
        expected_format: str = "json",
        max_retries: int = 2,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get structured output from the configured LLM provider"""
        return await self._client.analyze_with_structured_output(
            prompt=prompt,
            system=system,
            expected_format=expected_format,
            max_retries=max_retries,
            max_tokens=max_tokens
        )


# Global client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create global LLM client"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
