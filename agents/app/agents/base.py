"""Base agent class for all agents in the system"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

from app.integrations.llm_client import get_llm_client
from app.utils.logger import logger
from app.utils.helpers import generate_id
from app.utils.exceptions import AgentException


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.agent_id = generate_id(prefix=agent_name)
        self.llm_client = get_llm_client()
        logger.info(f"Initialized agent: {self.agent_name} ({self.agent_id})")
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and return results
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Processed results
        """
        pass
    
    async def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Call the LLM with a prompt
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Temperature override
            
        Returns:
            LLM response
        """
        try:
            logger.info(f"{self.agent_name}: Calling LLM")
            response = await self.llm_client.create_message(
                prompt=prompt,
                system=system_prompt,
                temperature=temperature
            )
            return response
        except Exception as e:
            logger.error(f"{self.agent_name}: LLM call failed: {e}")
            raise AgentException(f"{self.agent_name} failed: {e}")
    
    async def call_llm_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call the LLM and get structured JSON output
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            
        Returns:
            Structured output dictionary
        """
        try:
            logger.info(f"{self.agent_name}: Calling LLM for structured output")
            response = await self.llm_client.analyze_with_structured_output(
                prompt=prompt,
                system=system_prompt,
                expected_format="json"
            )
            return response
        except Exception as e:
            logger.error(f"{self.agent_name}: Structured LLM call failed: {e}")
            raise AgentException(f"{self.agent_name} structured call failed: {e}")
    
    def log(self, message: str, level: str = "info"):
        """Log a message with agent context"""
        log_func = getattr(logger, level, logger.info)
        log_func(f"[{self.agent_name}] {message}")
    
    def create_result(
        self,
        success: bool,
        data: Any = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized result dictionary
        
        Args:
            success: Whether the operation was successful
            data: Result data
            error: Error message if failed
            
        Returns:
            Standardized result dictionary
        """
        return {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "success": success,
            "data": data,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
