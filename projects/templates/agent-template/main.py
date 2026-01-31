#!/usr/bin/env python3
"""
Agent Template

A template for creating new GPT agents with the Aideck framework.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

# Import custom tools
from tools.custom_tools import *

from aideck.agent import GPTAgentBuilder


class TemplateAgent:
    """Template agent class."""

    def __init__(self):
        self.agent = None
        self.conversation_id = None

    async def initialize(self):
        """Initialize the agent."""
        print("🤖 Initializing Template Agent...")

        # Create agent with builder
        self.agent = (
            GPTAgentBuilder()
            .with_name("Template Agent")
            .with_description("A template agent for customization")
            .with_model("openai/gpt-4o")
            .with_temperature(0.7)
            .with_system_prompt(
                "You are a template AI agent. Customize this prompt "
                "to match your specific use case and requirements."
            )
            # Add your custom tools here
            # .with_tool(your_custom_tool)
            .with_memory(enabled=True, limit=5000)
            .with_streaming(enabled=True)
            .build()
        )

        # Initialize the agent
        await self.agent.initialize()

        # Create conversation
        self.conversation_id = self.agent.conversation_manager.create_conversation(
            title="Template Agent Session", tags=["template", "demo"]
        )

        print("✅ Template agent initialized successfully!")

    async def run(self):
        """Run the agent."""
        print("\n💬 Template Agent Ready!")
        print("Type 'quit' to exit.")
        print("-" * 30)

        while True:
            try:
                user_input = input("\n👤 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "quit":
                    print("\n👋 Goodbye!")
                    break

                # Process the message
                print("🤖 Agent: ", end="", flush=True)

                # Stream response
                response_text = ""
                async for chunk in self.agent.chat_stream(user_input):
                    print(chunk, end="", flush=True)
                    response_text += chunk

                print()  # New line after response

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


async def main():
    """Main function."""
    print("🚀 Starting Template Agent")
    print("=" * 30)

    try:
        # Create and run agent
        agent = TemplateAgent()
        await agent.initialize()
        await agent.run()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
