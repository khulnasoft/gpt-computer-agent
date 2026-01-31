#!/usr/bin/env python3
"""
Tool Integration Example

Advanced examples of tool integration with the GPT structure.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from aideck.agent import BaseTool, GPTAgentBuilder, ToolResult, tool


class FileSearchTool(BaseTool):
    """Tool for searching files in directories."""

    def __init__(self):
        super().__init__(
            name="file_search",
            description="Search for files in a directory with optional pattern matching",
        )

    async def execute(
        self, directory: str = ".", pattern: str = "*", recursive: bool = False
    ) -> ToolResult:
        """Search for files in a directory."""
        try:
            from pathlib import Path

            dir_path = Path(directory)
            if not dir_path.exists():
                return ToolResult(
                    success=False, error=f"Directory {directory} does not exist"
                )

            files = []
            if recursive:
                for file_path in dir_path.rglob(pattern):
                    if file_path.is_file():
                        files.append(str(file_path))
            else:
                for file_path in dir_path.glob(pattern):
                    if file_path.is_file():
                        files.append(str(file_path))

            return ToolResult(
                success=True,
                data={
                    "directory": directory,
                    "pattern": pattern,
                    "recursive": recursive,
                    "files_found": len(files),
                    "files": files[:20],  # Limit to 20 files
                },
            )

        except Exception as e:
            return ToolResult(success=False, error=f"Error searching files: {str(e)}")


class WebScraperTool(BaseTool):
    """Tool for scraping web content."""

    def __init__(self):
        super().__init__(
            name="web_scraper", description="Scrape content from a web page"
        )

    async def execute(self, url: str, selector: str = None) -> ToolResult:
        """Scrape content from a web page."""
        try:
            import requests
            from bs4 import BeautifulSoup

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            if selector:
                elements = soup.select(selector)
                content = [elem.get_text(strip=True) for elem in elements]
            else:
                # Get title and main content
                title = soup.title.string if soup.title else "No title"
                paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
                content = {
                    "title": title,
                    "content": paragraphs[:10],  # Limit to 10 paragraphs
                }

            return ToolResult(
                success=True,
                data={"url": url, "selector": selector, "content": content},
            )

        except Exception as e:
            return ToolResult(success=False, error=f"Error scraping {url}: {str(e)}")


class WeatherTool(BaseTool):
    """Tool for getting weather information."""

    def __init__(self):
        super().__init__(
            name="get_weather", description="Get weather information for a city"
        )

    async def execute(self, city: str, units: str = "metric") -> ToolResult:
        """Get weather information for a city."""
        try:
            # Mock weather data for demo
            weather_data = {
                "New York": {"temp": 22, "condition": "Sunny", "humidity": 65},
                "London": {"temp": 15, "condition": "Cloudy", "humidity": 80},
                "Tokyo": {"temp": 18, "condition": "Rainy", "humidity": 75},
                "Paris": {"temp": 20, "condition": "Partly cloudy", "humidity": 70},
                "Sydney": {"temp": 25, "condition": "Sunny", "humidity": 60},
            }

            if city not in weather_data:
                return ToolResult(
                    success=False, error=f"Weather data not available for {city}"
                )

            data = weather_data[city]
            temp_unit = "°C" if units == "metric" else "°F"

            return ToolResult(
                success=True,
                data={
                    "city": city,
                    "temperature": f"{data['temp']}{temp_unit}",
                    "condition": data["condition"],
                    "humidity": f"{data['humidity']}%",
                    "units": units,
                },
            )

        except Exception as e:
            return ToolResult(success=False, error=f"Error getting weather: {str(e)}")


@tool(name="json_analyzer", description="Analyze and validate JSON data")
def analyze_json(json_string: str) -> str:
    """Analyze and validate JSON data."""
    try:
        data = json.loads(json_string)

        analysis = {
            "valid": True,
            "type": type(data).__name__,
            "keys": list(data.keys()) if isinstance(data, dict) else "N/A",
            "length": len(data) if hasattr(data, "__len__") else "N/A",
            "size": len(json_string),
        }

        return f"JSON Analysis: {json.dumps(analysis, indent=2)}"

    except json.JSONDecodeError as e:
        return f"Invalid JSON: {str(e)}"


@tool(name="directory_tree", description="Generate a directory tree structure")
def generate_tree(directory: str = ".", max_depth: int = 3) -> str:
    """Generate a directory tree structure."""
    try:
        from pathlib import Path

        def build_tree(
            path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0
        ) -> list[str]:
            if current_depth >= max_depth:
                return []

            lines = []
            items = sorted(path.iterdir())

            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                lines.append(f"{prefix}{current_prefix}{item.name}")

                if item.is_dir():
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    lines.extend(
                        build_tree(item, next_prefix, max_depth, current_depth + 1)
                    )

            return lines

        dir_path = Path(directory)
        if not dir_path.exists():
            return f"Directory {directory} does not exist"

        tree_lines = [f"{directory}/"]
        tree_lines.extend(build_tree(dir_path, max_depth=max_depth))

        return "\n".join(tree_lines)

    except Exception as e:
        return f"Error generating tree: {str(e)}"


class ToolIntegrationAgent:
    """Agent with advanced tool integration."""

    def __init__(self):
        self.agent = None
        self.conversation_id = None

    async def initialize(self):
        """Initialize the agent with tools."""
        print("🔧 Initializing Tool Integration Agent...")

        # Create custom tools
        file_search_tool = FileSearchTool()
        web_scraper_tool = WebScraperTool()
        weather_tool = WeatherTool()

        # Create agent with builder
        self.agent = (
            GPTAgentBuilder()
            .with_name("Tool Integration Assistant")
            .with_description(
                "An AI assistant with advanced tool integration capabilities"
            )
            .with_model("openai/gpt-4o")
            .with_temperature(0.3)
            .with_system_prompt(
                "You are an advanced AI assistant with access to various tools. "
                "You can search files, scrape web content, get weather information, "
                "analyze JSON data, and generate directory trees. Use tools when helpful "
                "and provide detailed, informative responses. Always explain what tools "
                "you're using and why."
            )
            .with_tool(file_search_tool)
            .with_tool(web_scraper_tool)
            .with_tool(weather_tool)
            .with_tool(analyze_json)
            .with_tool(generate_tree)
            .with_memory(enabled=True, limit=8000)
            .with_streaming(enabled=True)
            .build()
        )

        # Initialize the agent
        await self.agent.initialize()

        # Create conversation
        self.conversation_id = self.agent.conversation_manager.create_conversation(
            title="Tool Integration Session",
            system_prompt="Demonstrating advanced tool integration capabilities.",
            tags=["tools", "integration", "demo"],
        )

        print("✅ Tool integration agent initialized successfully!")
        print(f"📝 Conversation ID: {self.conversation_id}")

        # Show available tools
        tools = self.agent.tool_registry.list_tools()
        print(f"🔧 Available tools: {', '.join(tools)}")

    async def demo_mode(self):
        """Run demonstration of tool capabilities."""
        print("\n🎭 Running Tool Integration Demo")
        print("=" * 50)

        demo_queries = [
            "What files are in the current directory?",
            "Generate a directory tree for the projects folder",
            "What's the weather like in Tokyo?",
            'Analyze this JSON: {"name": "test", "value": 42, "items": [1, 2, 3]}',
            "Search for all Python files in the src directory",
        ]

        for i, query in enumerate(demo_queries, 1):
            print(f"\n🔍 Demo {i}: {query}")
            print("-" * 30)

            try:
                print("🤖 Assistant: ", end="", flush=True)

                # Stream response
                response_text = ""
                async for chunk in self.agent.chat_stream(query):
                    print(chunk, end="", flush=True)
                    response_text += chunk

                print()  # New line after response

                # Add to conversation
                self.agent.conversation_manager.add_message(
                    self.conversation_id, "user", query
                )
                self.agent.conversation_manager.add_message(
                    self.conversation_id, "assistant", response_text
                )

            except Exception as e:
                print(f"❌ Error: {e}")

            print()  # Space between demos

    async def interactive_mode(self):
        """Interactive mode for custom queries."""
        print("\n💬 Interactive Tool Mode")
        print(
            "Type 'quit' to exit, 'demo' to run demos, 'tools' to see available tools"
        )
        print("-" * 50)

        while True:
            try:
                user_input = input("\n👤 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "quit":
                    print("\n👋 Goodbye!")
                    break

                if user_input.lower() == "demo":
                    await self.demo_mode()
                    continue

                if user_input.lower() == "tools":
                    await self.show_tools()
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

    async def show_tools(self):
        """Show available tools."""
        tools = self.agent.tool_registry.list_tools()
        print(f"\n🔧 Available Tools ({len(tools)}):")
        for tool_name in tools:
            tool = self.agent.tool_registry.get_tool(tool_name)
            if hasattr(tool, "description"):
                print(f"  • {tool_name}: {tool.description}")
            else:
                print(f"  • {tool_name}")

    async def show_stats(self):
        """Show agent statistics."""
        print("\n📊 Agent Statistics:")
        print("-" * 30)

        # Conversation stats
        conv_stats = self.agent.conversation_manager.get_conversation_stats(
            self.conversation_id
        )
        print(f"💬 Messages: {conv_stats['total_messages']}")

        # Tool stats
        if self.agent.tool_manager:
            tool_stats = self.agent.tool_manager.get_execution_history()
            print(f"🔧 Tool executions: {len(tool_stats)}")

            # Show recent tool usage
            if tool_stats:
                print("Recent tool calls:")
                for stat in tool_stats[-5:]:
                    print(
                        f"  • {stat['tool_name']}: {'✅' if stat['success'] else '❌'}"
                    )


async def main():
    """Main function."""
    print("🚀 Starting Tool Integration Example")
    print("=" * 50)

    try:
        # Create and initialize agent
        agent = ToolIntegrationAgent()
        await agent.initialize()

        # Ask user for mode
        mode = input("\nChoose mode (demo/interactive): ").strip().lower()

        if mode == "demo":
            await agent.demo_mode()
        else:
            await agent.interactive_mode()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
