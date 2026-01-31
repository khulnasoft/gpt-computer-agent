#!/usr/bin/env python3
"""
Basic Chat Agent Example

A simple conversational agent demonstrating the GPT structure functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from aideck.agent import GPTAgentBuilder, tool


@tool(name="get_time", description="Get the current time")
def get_current_time() -> str:
    """Get the current time and date."""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool(name="calculate", description="Perform basic mathematical calculations")
def calculate(expression: str) -> str:
    """
    Calculate the result of a mathematical expression.

    Args:
        expression: A mathematical expression (e.g., "2 + 3 * 4")

    Returns:
        The result of the calculation
    """
    try:
        # Safe evaluation
        import ast
        import operator

        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
        }

        def eval_node(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.BinOp):
                left = eval_node(node.left)
                right = eval_node(node.right)
                op_type = type(node.op)
                return operators[op_type](left, right)
            else:
                raise ValueError(f"Unsupported operation: {type(node)}")

        tree = ast.parse(expression, mode="eval")
        result = eval_node(tree.body)
        return str(result)

    except Exception as e:
        return f"Error: {str(e)}"


class BasicChatAgent:
    """Basic chat agent with GPT structure."""

    def __init__(self):
        self.agent = None
        self.conversation_id = None

    async def initialize(self):
        """Initialize the chat agent."""
        print("🤖 Initializing Basic Chat Agent...")

        # Create agent with builder
        self.agent = (
            GPTAgentBuilder()
            .with_name("Basic Chat Assistant")
            .with_description("A helpful AI assistant for basic conversations")
            .with_model("openai/gpt-4o")
            .with_temperature(0.7)
            .with_system_prompt(
                "You are a helpful AI assistant. You can help with conversations, "
                "answer questions, tell jokes, and use available tools when needed. "
                "Be friendly, concise, and helpful."
            )
            .with_tool(get_current_time)
            .with_tool(calculate)
            .with_memory(enabled=True, limit=5000)
            .with_streaming(enabled=True)
            .build()
        )

        # Initialize the agent
        await self.agent.initialize()

        # Create conversation
        self.conversation_id = self.agent.conversation_manager.create_conversation(
            title="Basic Chat Session",
            system_prompt="You are having a friendly conversation with a user.",
            tags=["chat", "basic"],
        )

        print("✅ Chat agent initialized successfully!")
        print(f"📝 Conversation ID: {self.conversation_id}")

    async def chat_loop(self):
        """Main chat loop."""
        print(
            "\n💬 Chat started! Type 'quit' to exit, 'clear' to clear memory, 'history' to see history."
        )
        print("-" * 50)

        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "quit":
                    print("\n👋 Goodbye!")
                    break

                if user_input.lower() == "clear":
                    await self.clear_memory()
                    continue

                if user_input.lower() == "history":
                    await self.show_history()
                    continue

                if user_input.lower() == "stats":
                    await self.show_stats()
                    continue

                # Process the message
                print("🤖 Assistant: ", end="", flush=True)

                # Stream response
                response_text = ""
                async for chunk in self.agent.chat_stream(user_input):
                    print(chunk, end="", flush=True)
                    response_text += chunk

                print()  # New line after response

                # Add to conversation
                self.agent.conversation_manager.add_message(
                    self.conversation_id, "user", user_input
                )
                self.agent.conversation_manager.add_message(
                    self.conversation_id, "assistant", response_text
                )

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

    async def clear_memory(self):
        """Clear conversation memory."""
        if self.agent.memory:
            self.agent.memory.clear()
            print("🧹 Memory cleared!")
        else:
            print("ℹ️ No memory to clear.")

    async def show_history(self):
        """Show conversation history."""
        messages = self.agent.conversation_manager.get_conversation_messages(
            self.conversation_id, limit=10
        )

        if not messages:
            print("📝 No conversation history yet.")
            return

        print("\n📜 Conversation History:")
        print("-" * 30)

        for msg in messages[-10:]:
            role_emoji = {"user": "👤", "assistant": "🤖", "system": "⚙️"}.get(
                msg.role.value, "❓"
            )
            content = (
                msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            )
            print(f"{role_emoji} {msg.role.value.title()}: {content}")

    async def show_stats(self):
        """Show agent statistics."""
        print("\n📊 Agent Statistics:")
        print("-" * 30)

        # Conversation stats
        conv_stats = self.agent.conversation_manager.get_conversation_stats(
            self.conversation_id
        )
        print(f"💬 Messages: {conv_stats['total_messages']}")
        print(f"🏷️ Tags: {', '.join(conv_stats['tags'])}")

        # Tool stats
        if self.agent.tool_manager:
            tool_stats = self.agent.tool_manager.get_execution_history(limit=5)
            print(f"🔧 Recent tool calls: {len(tool_stats)}")

        # Memory stats
        if self.agent.memory_manager:
            memory_stats = await self.agent.memory_manager.get_memory_stats()
            print(f"🧠 Memories: {memory_stats['total_memories']}")


async def main():
    """Main function."""
    print("🚀 Starting Basic Chat Agent Example")
    print("=" * 50)

    try:
        # Create and initialize agent
        chat_agent = BasicChatAgent()
        await chat_agent.initialize()

        # Start chat loop
        await chat_agent.chat_loop()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
