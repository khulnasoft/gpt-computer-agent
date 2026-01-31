#!/usr/bin/env python3
"""
Test script for the GPT structure implementation.

This script demonstrates and tests the comprehensive GPT agent system
including tools, conversations, memory, and response processing.
"""

import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from aideck.agent import (
    ConversationManager,
    GPTAgentBuilder,
    MemoryManager,
    MemoryPriority,
    MemoryType,
    ResponseProcessor,
    ToolManager,
    tool,
)


@tool(name="echo", description="Echo back the input text")
def echo_tool(text: str) -> str:
    """Echo the input text back to the user."""
    return f"Echo: {text}"


@tool(name="add_numbers", description="Add two numbers together")
def add_numbers(a: float, b: float) -> float:
    """Add two numbers and return the result."""
    return a + b


@tool(name="get_weather", description="Get mock weather information")
def get_weather(city: str) -> str:
    """Get mock weather information for a city."""
    weather_data = {
        "New York": "Sunny, 72°F",
        "London": "Cloudy, 59°F",
        "Tokyo": "Rainy, 65°F",
        "Paris": "Partly cloudy, 68°F",
    }
    return weather_data.get(city, f"Weather data not available for {city}")


async def test_tool_system():
    """Test the tool system."""
    print("🔧 Testing Tool System...")

    # Create tool manager
    tool_manager = ToolManager()

    # Register tools
    tool_manager.register_function(echo_tool)
    tool_manager.register_function(add_numbers)
    tool_manager.register_function(get_weather)

    # List tools
    tools = tool_manager.registry.list_tools()
    print(f"✅ Registered {len(tools)} tools: {tools}")

    # Test tool execution
    result1 = await tool_manager.execute_tool_call("echo", {"text": "Hello World"})
    print(f"✅ Echo result: {result1.data}")

    result2 = await tool_manager.execute_tool_call("add_numbers", {"a": 5, "b": 3})
    print(f"✅ Addition result: {result2.data}")

    result3 = await tool_manager.execute_tool_call("get_weather", {"city": "New York"})
    print(f"✅ Weather result: {result3.data}")

    # Get execution history
    history = tool_manager.get_execution_history()
    print(f"✅ Execution history contains {len(history)} entries")

    return tool_manager


async def test_conversation_system():
    """Test the conversation system."""
    print("\n💬 Testing Conversation System...")

    # Create conversation manager
    conv_manager = ConversationManager()

    # Create a new conversation
    conv_id = conv_manager.create_conversation(
        title="Test Conversation",
        system_prompt="You are a helpful AI assistant.",
        tags=["test", "demo"],
    )
    print(f"✅ Created conversation: {conv_id}")

    # Add messages
    conv_manager.add_message(conv_id, "user", "Hello, how are you?")
    conv_manager.add_message(conv_id, "assistant", "I'm doing well, thank you!")
    conv_manager.add_message(conv_id, "user", "What can you help me with?")

    # Get conversation messages
    messages = conv_manager.get_conversation_messages(conv_id)
    print(f"✅ Conversation has {len(messages)} messages")

    # Get context messages
    context = conv_manager.get_context_messages(conv_id)
    print(f"✅ Context contains {len(context)} messages")

    # Get conversation stats
    stats = conv_manager.get_conversation_stats(conv_id)
    print(
        f"✅ Conversation stats: {stats['total_messages']} messages, {len(stats['role_counts'])} roles"
    )

    # List conversations
    conversations = conv_manager.list_conversations()
    print(f"✅ Found {len(conversations)} conversations")

    return conv_manager


async def test_memory_system():
    """Test the memory system."""
    print("\n🧠 Testing Memory System...")

    # Create memory manager
    memory_manager = MemoryManager()

    # Add different types of memories
    await memory_manager.add_memory(
        "User prefers Python over JavaScript",
        MemoryType.LONG_TERM,
        MemoryPriority.HIGH,
        tags=["preferences", "programming"],
    )

    await memory_manager.add_memory(
        "Current conversation about testing",
        MemoryType.SHORT_TERM,
        MemoryPriority.MEDIUM,
        tags=["conversation", "testing"],
    )

    await memory_manager.add_memory(
        "User asked about weather in New York",
        MemoryType.EPISODIC,
        MemoryPriority.MEDIUM,
        tags=["weather", "new_york"],
    )

    # Search memories
    results = await memory_manager.search_memories("Python programming", limit=5)
    print(f"✅ Found {len(results)} memories for 'Python programming'")
    for result in results:
        print(
            f"   - {result.memory_item.content[:50]}... (score: {result.relevance_score:.2f})"
        )

    # Get context memories
    context_memories = await memory_manager.get_context_memories(max_tokens=100)
    print(f"✅ Retrieved {len(context_memories)} memories for context")

    # Get memory stats
    stats = await memory_manager.get_memory_stats()
    print(f"✅ Memory stats: {stats['total_memories']} total memories")

    return memory_manager


async def test_agent_builder():
    """Test the GPT agent builder."""
    print("\n🤖 Testing GPT Agent Builder...")

    # Create agent using builder
    agent = (
        GPTAgentBuilder()
        .with_name("Test Assistant")
        .with_description("A test assistant for demonstration")
        .with_model("openai/gpt-4o")
        .with_temperature(0.7)
        .with_system_prompt("You are a helpful test assistant.")
        .with_tool(echo_tool)
        .with_tool(add_numbers)
        .with_memory(enabled=True, limit=5000)
        .with_streaming(enabled=True)
        .build()
    )

    print(f"✅ Created agent: {agent.config.name}")
    print(f"✅ Model: {agent.config.model_provider}")
    print(f"✅ Tools: {agent.tool_registry.list_tools()}")
    print(f"✅ Memory enabled: {agent.config.enable_memory}")

    return agent


async def test_integration():
    """Test integrated system functionality."""
    print("\n🔗 Testing Integrated System...")

    # Create components
    tool_manager = ToolManager()
    tool_manager.register_function(echo_tool)
    tool_manager.register_function(add_numbers)

    conv_manager = ConversationManager()
    conv_id = conv_manager.create_conversation(title="Integration Test")

    response_processor = ResponseProcessor(tool_manager, conv_manager)

    # Mock a response with tool calls
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": "I'll help you add those numbers.",
                    "tool_calls": [
                        {
                            "id": "call_123",
                            "function": {
                                "name": "add_numbers",
                                "arguments": '{"a": 10, "b": 25}',
                            },
                        }
                    ],
                }
            }
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 15, "total_tokens": 35},
    }

    # Process the response
    processed = await response_processor.process_response(mock_response, conv_id)
    print(f"✅ Processed response type: {processed.response_type.value}")
    print(f"✅ Content: {processed.content}")
    print(f"✅ Tool calls: {len(processed.tool_calls) if processed.tool_calls else 0}")

    # Handle the response (execute tools)
    response_content, tool_results = await response_processor.handle_response(
        processed, conv_id, auto_execute_tools=True
    )

    print(f"✅ Final response: {response_content}")
    print(f"✅ Tool execution results: {len(tool_results) if tool_results else 0}")

    if tool_results:
        for result in tool_results:
            print(f"   - {result.tool_call.name}: {result.result.data}")

    # Get tool usage stats
    stats = response_processor.get_tool_usage_stats()
    print(f"✅ Tool usage stats: {stats}")


async def main():
    """Run all tests."""
    print("🚀 Starting GPT Structure Tests...\n")

    try:
        # Test individual components
        tool_manager = await test_tool_system()
        conv_manager = await test_conversation_system()
        memory_manager = await test_memory_system()
        agent = await test_agent_builder()

        # Test integration
        await test_integration()

        print("\n✅ All tests completed successfully!")
        print("\n📊 Summary:")
        print(
            f"   - Tool System: {len(tool_manager.registry.list_tools())} tools registered"
        )
        print(
            f"   - Conversation System: {len(conv_manager.list_conversations())} conversations"
        )
        print(
            f"   - Memory System: {(await memory_manager.get_memory_stats())['total_memories']} memories"
        )
        print(f"   - Agent Builder: {agent.config.name} created successfully")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
