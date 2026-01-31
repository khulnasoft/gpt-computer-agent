"""
Agent Tests

Test cases for the template agent.
"""

import sys
from pathlib import Path

import pytest

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "src"))

from main import TemplateAgent


class TestTemplateAgent:
    """Test cases for TemplateAgent."""

    @pytest.fixture
    async def agent(self):
        """Create a test agent instance."""
        agent = TemplateAgent()
        await agent.initialize()
        return agent

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test that agent initializes correctly."""
        assert agent.agent is not None
        assert agent.conversation_id is not None
        assert agent.agent.config.name == "Template Agent"

    @pytest.mark.asyncio
    async def test_basic_chat(self, agent):
        """Test basic chat functionality."""
        response = await agent.agent.chat("Hello, how are you?")
        assert response is not None
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_memory_functionality(self, agent):
        """Test memory functionality."""
        # Add a test message
        agent.agent.conversation_manager.add_message(
            agent.conversation_id, "user", "Test message for memory"
        )

        # Check that message was added
        messages = agent.agent.conversation_manager.get_conversation_messages(
            agent.conversation_id
        )
        assert len(messages) > 0
        assert any(msg.content == "Test message for memory" for msg in messages)


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
