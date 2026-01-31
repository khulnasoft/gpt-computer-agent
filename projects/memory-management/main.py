#!/usr/bin/env python3
"""
Memory Management Example

Demonstration of the advanced memory management system.
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from aideck.agent import (
    GPTAgentBuilder,
    MemoryConfig,
    MemoryManager,
    MemoryPriority,
    MemoryType,
)


class MemoryDemo:
    """Demonstration of memory management capabilities."""

    def __init__(self):
        self.memory_manager = None
        self.agent = None

    async def initialize(self):
        """Initialize memory manager and agent."""
        print("🧠 Initializing Memory Management Demo...")

        # Create memory manager with custom config
        config = MemoryConfig(
            max_short_term_items=50,
            max_long_term_items=200,
            default_ttl_hours=24,
            enable_semantic_search=True,
            similarity_threshold=0.6,
            max_context_items=15,
        )

        self.memory_manager = MemoryManager(config=config)

        # Create agent with memory integration
        self.agent = (
            GPTAgentBuilder()
            .with_name("Memory Assistant")
            .with_description("An AI assistant with advanced memory capabilities")
            .with_model("openai/gpt-4o")
            .with_temperature(0.5)
            .with_system_prompt(
                "You are an AI assistant with excellent memory capabilities. "
                "You remember previous conversations, user preferences, and "
                "can search through your memories to provide better responses. "
                "Always reference relevant memories when helpful."
            )
            .with_memory(enabled=True, limit=10000)
            .build()
        )

        await self.agent.initialize()

        print("✅ Memory management system initialized!")

    async def demo_memory_types(self):
        """Demonstrate different memory types."""
        print("\n📚 Demonstrating Memory Types")
        print("=" * 40)

        # Short-term memory
        print("\n🔄 Adding Short-term Memory:")
        await self.memory_manager.add_memory(
            "User is currently working on a Python project",
            MemoryType.SHORT_TERM,
            MemoryPriority.MEDIUM,
            tags=["current", "project", "python"],
        )

        await self.memory_manager.add_memory(
            "Current conversation about memory management",
            MemoryType.SHORT_TERM,
            MemoryPriority.HIGH,
            tags=["conversation", "memory", "demo"],
        )

        # Long-term memory
        print("\n💾 Adding Long-term Memory:")
        await self.memory_manager.add_memory(
            "User prefers Python over JavaScript for backend development",
            MemoryType.LONG_TERM,
            MemoryPriority.HIGH,
            tags=["preferences", "programming", "python"],
            user_id="demo_user",
        )

        await self.memory_manager.add_memory(
            "User has 5 years of software development experience",
            MemoryType.LONG_TERM,
            MemoryPriority.HIGH,
            tags=["experience", "background"],
            user_id="demo_user",
        )

        # Episodic memory
        print("\n🎬 Adding Episodic Memory:")
        await self.memory_manager.add_memory(
            "User asked about memory management on 2025-01-30",
            MemoryType.EPISODIC,
            MemoryPriority.MEDIUM,
            tags=["question", "memory", "date"],
            conversation_id="conv_001",
        )

        await self.memory_manager.add_memory(
            "User successfully implemented tool integration yesterday",
            MemoryType.EPISODIC,
            MemoryPriority.HIGH,
            tags=["achievement", "tools", "success"],
            conversation_id="conv_002",
        )

        # Semantic memory
        print("\n🧠 Adding Semantic Memory:")
        await self.memory_manager.add_memory(
            "Memory management in AI systems involves storing, retrieving, and optimizing information",
            MemoryType.SEMANTIC,
            MemoryPriority.MEDIUM,
            tags=["definition", "ai", "memory"],
        )

        await self.memory_manager.add_memory(
            "Semantic search uses embeddings to find similar content based on meaning",
            MemoryType.SEMANTIC,
            MemoryPriority.MEDIUM,
            tags=["definition", "search", "embeddings"],
        )

        print("✅ Added memories to all types!")

    async def demo_memory_search(self):
        """Demonstrate memory search capabilities."""
        print("\n🔍 Demonstrating Memory Search")
        print("=" * 40)

        search_queries = [
            "Python programming",
            "user preferences",
            "memory management",
            "recent achievements",
        ]

        for query in search_queries:
            print(f"\n🔎 Searching for: '{query}'")
            results = await self.memory_manager.search_memories(
                query, limit=5, include_content=True
            )

            if results:
                print(f"Found {len(results)} relevant memories:")
                for i, result in enumerate(results, 1):
                    memory = result.memory_item
                    print(
                        f"  {i}. [{memory.memory_type.value}] {memory.content[:60]}..."
                    )
                    print(
                        f"     Score: {result.relevance_score:.2f} | Reasons: {', '.join(result.match_reasons)}"
                    )
            else:
                print("  No relevant memories found.")

    async def demo_context_optimization(self):
        """Demonstrate context optimization."""
        print("\n⚡ Demonstrating Context Optimization")
        print("=" * 40)

        # Get context memories
        context_memories = await self.memory_manager.get_context_memories(
            max_tokens=500
        )

        print(f"Retrieved {len(context_memories)} memories for context:")
        for i, memory in enumerate(context_memories, 1):
            print(f"  {i}. [{memory.memory_type.value}] {memory.content[:50]}...")

        # Show context score calculation
        print("\n📊 Context Scores:")
        for memory in context_memories[:5]:  # Show top 5
            score = self._calculate_context_score(memory)
            print(f"  {memory.content[:40]}... - Score: {score:.1f}")

    def _calculate_context_score(self, memory) -> float:
        """Calculate context score for a memory."""
        score = 0.0

        # Priority scoring
        priority_scores = {
            MemoryPriority.LOW: 1,
            MemoryPriority.MEDIUM: 2,
            MemoryPriority.HIGH: 3,
            MemoryPriority.CRITICAL: 4,
        }
        score += priority_scores[memory.priority]

        # Recency scoring
        days_old = (datetime.now(timezone.utc) - memory.created_at).days
        recency_score = max(0, 10 - days_old)
        score += recency_score

        # Access frequency scoring
        access_score = min(5, memory.access_count)
        score += access_score

        return score

    async def demo_memory_analytics(self):
        """Demonstrate memory analytics."""
        print("\n📈 Demonstrating Memory Analytics")
        print("=" * 40)

        # Get memory statistics
        stats = await self.memory_manager.get_memory_stats()

        print("📊 Memory Statistics:")
        print(f"  Total memories: {stats['total_memories']}")
        print(f"  Expired memories: {stats['expired_count']}")
        print(f"  Average access count: {stats['average_access_count']:.2f}")

        if stats["oldest_memory"]:
            print(f"  Oldest memory: {stats['oldest_memory'][:10]}...")
        if stats["newest_memory"]:
            print(f"  Newest memory: {stats['newest_memory'][:10]}...")

        print("\n📋 By Type:")
        for memory_type, count in stats["by_type"].items():
            print(f"  {memory_type}: {count}")

        print("\n🎯 By Priority:")
        for priority, count in stats["by_priority"].items():
            print(f"  {priority}: {count}")

    async def demo_memory_cleanup(self):
        """Demonstrate memory cleanup."""
        print("\n🧹 Demonstrating Memory Cleanup")
        print("=" * 40)

        # Add some expired memories
        past_time = datetime.now(timezone.utc) - timedelta(hours=25)

        await self.memory_manager.add_memory(
            "This memory should be expired",
            MemoryType.SHORT_TERM,
            MemoryPriority.LOW,
            expires_at=past_time,
        )

        print("Added expired memory for cleanup demo")

        # Get stats before cleanup
        stats_before = await self.memory_manager.get_memory_stats()
        print(f"Memories before cleanup: {stats_before['total_memories']}")

        # Run cleanup
        cleaned_count = await self.memory_manager.cleanup_expired_memories()
        print(f"Cleaned up {cleaned_count} expired memories")

        # Get stats after cleanup
        stats_after = await self.memory_manager.get_memory_stats()
        print(f"Memories after cleanup: {stats_after['total_memories']}")

    async def interactive_memory_demo(self):
        """Interactive memory demonstration."""
        print("\n💬 Interactive Memory Demo")
        print("Commands: 'add', 'search', 'stats', 'context', 'cleanup', 'quit'")
        print("-" * 50)

        while True:
            try:
                command = input("\n👤 Command: ").strip().lower()

                if not command:
                    continue

                if command == "quit":
                    print("\n👋 Goodbye!")
                    break

                if command == "add":
                    await self.interactive_add_memory()

                elif command == "search":
                    await self.interactive_search()

                elif command == "stats":
                    await self.demo_memory_analytics()

                elif command == "context":
                    await self.demo_context_optimization()

                elif command == "cleanup":
                    await self.demo_memory_cleanup()

                else:
                    print(
                        "Unknown command. Try: add, search, stats, context, cleanup, quit"
                    )

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    async def interactive_add_memory(self):
        """Interactive memory addition."""
        print("\n➕ Add New Memory")

        content = input("Content: ").strip()
        if not content:
            print("Content cannot be empty!")
            return

        print("Memory types:", [t.value for t in MemoryType])
        memory_type_str = input("Memory type (short_term): ").strip() or "short_term"

        try:
            memory_type = MemoryType(memory_type_str)
        except ValueError:
            print("Invalid memory type, using short_term")
            memory_type = MemoryType.SHORT_TERM

        print("Priorities:", [p.value for p in MemoryPriority])
        priority_str = input("Priority (medium): ").strip() or "medium"

        try:
            priority = MemoryPriority(priority_str)
        except ValueError:
            print("Invalid priority, using medium")
            priority = MemoryPriority.MEDIUM

        tags_input = input("Tags (comma-separated): ").strip()
        tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []

        await self.memory_manager.add_memory(
            content=content, memory_type=memory_type, priority=priority, tags=tags
        )

        print("✅ Memory added successfully!")

    async def interactive_search(self):
        """Interactive memory search."""
        query = input("\n🔍 Search query: ").strip()
        if not query:
            print("Query cannot be empty!")
            return

        results = await self.memory_manager.search_memories(query, limit=10)

        if results:
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                memory = result.memory_item
                print(f"\n{i}. [{memory.memory_type.value}] {memory.content}")
                print(f"   Score: {result.relevance_score:.2f}")
                print(f"   Tags: {', '.join(memory.tags)}")
                print(f"   Created: {memory.created_at.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("No results found.")


async def main():
    """Main function."""
    print("🚀 Starting Memory Management Example")
    print("=" * 50)

    try:
        # Create and initialize demo
        demo = MemoryDemo()
        await demo.initialize()

        # Run demonstrations
        await demo.demo_memory_types()
        await demo.demo_memory_search()
        await demo.demo_context_optimization()
        await demo.demo_memory_analytics()
        await demo.demo_memory_cleanup()

        # Interactive mode
        await demo.interactive_memory_demo()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
