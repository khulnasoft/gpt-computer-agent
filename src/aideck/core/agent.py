import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel

from ..config.settings import settings
from ..utils.tools import Tool, ToolRegistry


@dataclass
class AgentConfig:
    """Configuration for the agent."""

    name: str = "GPT Computer Agent"
    description: str = "An intelligent agent that can perform various tasks"
    llm_provider: str = settings.LLM_PROVIDER
    max_iterations: int = 10
    temperature: float = 0.7
    tools: list[Tool | type[BaseModel]] = field(default_factory=list)
    verbose: bool = False


class BaseAgent:
    """Base class for all agents."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.tool_registry = ToolRegistry()
        self.setup_tools()
        self.setup_llm()

    def setup_tools(self) -> None:
        """Register tools with the agent."""
        for tool in self.config.tools:
            if isinstance(tool, Tool):
                self.tool_registry.register(tool)
            elif hasattr(tool, "run") and callable(tool.run):
                self.tool_registry.register(tool)

        logger.info(f"Registered {len(self.tool_registry)} tools")

    def setup_llm(self) -> None:
        """Initialize the language model."""
        # This will be implemented by subclasses
        pass

    async def run(self, input_data: str | dict[str, Any]) -> Any:
        """Run the agent with the given input."""
        raise NotImplementedError("Subclasses must implement this method")

    def save_state(self, path: str | Path) -> None:
        """Save the agent's state to a file."""
        state = {
            "config": self.config.__dict__,
            "tools": [tool.name for tool in self.tool_registry.tools.values()],
        }

        with open(path, "w") as f:
            json.dump(state, f, indent=2)

        logger.info(f"Saved agent state to {path}")

    @classmethod
    def load_state(cls, path: str | Path):
        """Load an agent from a saved state."""
        with open(path) as f:
            state = json.load(f)

        config = AgentConfig(**state["config"])
        return cls(config)


class GPTChatAgent(BaseAgent):
    """An agent that uses OpenAI's GPT models for chat-based interactions."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.messages = []

    def setup_llm(self) -> None:
        """Initialize the OpenAI client."""
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())
        except ImportError:
            logger.error(
                "OpenAI package not installed. Install with: pip install openai"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    async def run(self, message: str) -> str:
        """Run the agent with the given message."""
        self.messages.append({"role": "user", "content": message})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=self.messages,
                temperature=self.config.temperature,
                max_tokens=1000,
                tools=[tool.to_dict() for tool in self.tool_registry.tools.values()],
                tool_choice="auto",
            )

            # Process the response
            response_message = response.choices[0].message
            self.messages.append(response_message)

            # Check if the model wants to call a function
            if hasattr(response_message, "tool_calls") and response_message.tool_calls:
                tool_calls = response_message.tool_calls
                self.messages.append(
                    {"role": "agent", "content": None, "tool_calls": tool_calls}
                )

                # Process each tool call
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Call the function
                    tool = self.tool_registry.get_tool(function_name)
                    if tool:
                        function_response = tool.run(**function_args)
                        self.messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": json.dumps(function_response),
                            }
                        )

                # Get a new response with the function call results
                second_response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=self.messages,
                )
                response_message = second_response.choices[0].message
                self.messages.append(response_message)

            return response_message.content

        except Exception as e:
            logger.error(f"Error in agent run: {e}")
            raise
