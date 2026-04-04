"""Base agent tests"""
import pytest
from app.agents.base import BaseAgent
from app.utils.exceptions import AgentException


class TestAgent(BaseAgent):
    """Test agent implementation"""
    
    def __init__(self):
        super().__init__("test_agent")
    
    async def process(self, input_data):
        """Test process method"""
        return {"result": "test"}


@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization"""
    agent = TestAgent()
    assert agent.agent_name == "test_agent"
    assert agent.agent_id.startswith("test_agent_")
    assert len(agent.agent_id) > len("test_agent_")


@pytest.mark.asyncio
async def test_create_result_success():
    """Test creating successful result"""
    agent = TestAgent()
    result = agent.create_result(success=True, data={"test": "data"})
    
    assert result["success"] is True
    assert result["data"]["test"] == "data"
    assert result["agent_name"] == "test_agent"
    assert "agent_id" in result
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_create_result_failure():
    """Test creating failure result"""
    agent = TestAgent()
    result = agent.create_result(success=False, error="Test error")
    
    assert result["success"] is False
    assert result["error"] == "Test error"
    assert result["agent_name"] == "test_agent"


@pytest.mark.asyncio
async def test_agent_logging():
    """Test agent logging functionality"""
    agent = TestAgent()
    
    # Should not raise exception
    agent.log("Test message")
    agent.log("Warning message", level="warning")
    agent.log("Error message", level="error")


@pytest.mark.asyncio
async def test_agent_process():
    """Test agent process method"""
    agent = TestAgent()
    result = await agent.process({"input": "test"})
    
    assert result == {"result": "test"}
