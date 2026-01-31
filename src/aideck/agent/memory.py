"""
Memory Management System for GPT Agents

This module provides comprehensive memory management capabilities including
short-term memory, long-term memory, semantic search, and context optimization.
"""

import asyncio
import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Types of memory storage."""

    SHORT_TERM = "short_term"  # Current conversation context
    LONG_TERM = "long_term"  # Persistent knowledge
    EPISODIC = "episodic"  # Specific events/experiences
    SEMANTIC = "semantic"  # General knowledge
    WORKING = "working"  # Temporary processing memory


class MemoryPriority(str, Enum):
    """Priority levels for memory items."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MemoryItem:
    """Represents a single memory item."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    memory_type: MemoryType = MemoryType.SHORT_TERM
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    priority: MemoryPriority = MemoryPriority.MEDIUM
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime | None = None
    access_count: int = 0
    last_accessed: datetime | None = None
    tags: list[str] = field(default_factory=list)
    embedding: list[float] | None = None  # For semantic search
    conversation_id: str | None = None
    user_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "access_count": self.access_count,
            "last_accessed": (
                self.last_accessed.isoformat() if self.last_accessed else None
            ),
            "tags": self.tags,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryItem":
        """Create from dictionary."""
        item = cls(
            id=data["id"],
            memory_type=MemoryType(data["memory_type"]),
            content=data["content"],
            metadata=data["metadata"],
            priority=MemoryPriority(data["priority"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            expires_at=(
                datetime.fromisoformat(data["expires_at"])
                if data["expires_at"]
                else None
            ),
            access_count=data["access_count"],
            tags=data["tags"],
            conversation_id=data.get("conversation_id"),
            user_id=data.get("user_id"),
        )

        if data.get("last_accessed"):
            item.last_accessed = datetime.fromisoformat(data["last_accessed"])

        return item


class MemorySearchResult(BaseModel):
    """Result of a memory search."""

    memory_item: MemoryItem
    relevance_score: float
    match_reasons: list[str] = Field(default_factory=list)


class MemoryConfig(BaseModel):
    """Configuration for memory management."""

    max_short_term_items: int = 1000
    max_long_term_items: int = 10000
    default_ttl_hours: int = 24 * 7  # 1 week
    cleanup_interval_hours: int = 1
    enable_semantic_search: bool = True
    embedding_model: str = "text-embedding-ada-002"
    similarity_threshold: float = 0.7
    max_context_items: int = 20
    prioritize_recent: bool = True
    prioritize_accessed: bool = True


class MemoryManager:
    """
    Comprehensive memory management system for GPT agents.

    Features:
    - Multiple memory types (short-term, long-term, episodic, semantic, working)
    - Automatic cleanup and expiration
    - Semantic search capabilities
    - Priority-based management
    - Context optimization
    - Persistent storage
    """

    def __init__(
        self, config: MemoryConfig | None = None, storage_path: Path | None = None
    ):
        self.config = config or MemoryConfig()
        self.storage_path = storage_path
        self.memories: dict[MemoryType, list[MemoryItem]] = {
            memory_type: [] for memory_type in MemoryType
        }
        self.indexes: dict[str, dict[str, list[str]]] = {
            "tags": {},
            "conversation_id": {},
            "user_id": {},
            "content_hash": {},
        }
        self._cleanup_task: asyncio.Task | None = None

        # Load existing memories if storage path is provided
        if self.storage_path:
            self._load_memories()

        # Start cleanup task
        self._start_cleanup_task()

    async def add_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        expires_at: datetime | None = None,
        conversation_id: str | None = None,
        user_id: str | None = None,
    ) -> MemoryItem:
        """
        Add a new memory item.

        Args:
            content: The content to store
            memory_type: Type of memory
            priority: Priority level
            metadata: Additional metadata
            tags: Tags for categorization
            expires_at: Expiration time
            conversation_id: Associated conversation
            user_id: Associated user

        Returns:
            The created memory item
        """
        memory_item = MemoryItem(
            content=content,
            memory_type=memory_type,
            priority=priority,
            metadata=metadata or {},
            tags=tags or [],
            expires_at=expires_at
            or (
                datetime.now(timezone.utc)
                + timedelta(hours=self.config.default_ttl_hours)
            ),
            conversation_id=conversation_id,
            user_id=user_id,
        )

        # Add to appropriate memory store
        self.memories[memory_type].append(memory_item)

        # Update indexes
        self._update_indexes(memory_item)

        # Generate embedding if semantic search is enabled
        if self.config.enable_semantic_search:
            await self._generate_embedding(memory_item)

        # Enforce size limits
        await self._enforce_size_limits(memory_type)

        # Save to storage
        if self.storage_path:
            await self._save_memory(memory_item)

        logger.debug(f"Added {memory_type.value} memory: {memory_item.id}")
        return memory_item

    async def get_memory(self, memory_id: str) -> MemoryItem | None:
        """Get a memory item by ID."""
        for memory_list in self.memories.values():
            for memory in memory_list:
                if memory.id == memory_id:
                    # Update access statistics
                    memory.access_count += 1
                    memory.last_accessed = datetime.now(timezone.utc)
                    return memory
        return None

    async def update_memory(
        self,
        memory_id: str,
        content: str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
        priority: MemoryPriority | None = None,
    ) -> MemoryItem | None:
        """Update an existing memory item."""
        memory = await self.get_memory(memory_id)
        if not memory:
            return None

        # Update fields
        if content is not None:
            memory.content = content
        if metadata is not None:
            memory.metadata.update(metadata)
        if tags is not None:
            memory.tags = tags
        if priority is not None:
            memory.priority = priority

        memory.updated_at = datetime.now(timezone.utc)

        # Regenerate embedding if content changed
        if content is not None and self.config.enable_semantic_search:
            await self._generate_embedding(memory)

        # Update indexes
        self._update_indexes(memory)

        # Save to storage
        if self.storage_path:
            await self._save_memory(memory)

        return memory

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory item."""
        for memory_type, memory_list in self.memories.items():
            for i, memory in enumerate(memory_list):
                if memory.id == memory_id:
                    # Remove from memory list
                    del memory_list[i]

                    # Remove from indexes
                    self._remove_from_indexes(memory)

                    # Delete from storage
                    if self.storage_path:
                        await self._delete_memory_storage(memory_id)

                    logger.debug(f"Deleted memory: {memory_id}")
                    return True
        return False

    async def search_memories(
        self,
        query: str,
        memory_types: list[MemoryType] | None = None,
        tags: list[str] | None = None,
        conversation_id: str | None = None,
        user_id: str | None = None,
        limit: int = 10,
        include_content: bool = True,
    ) -> list[MemorySearchResult]:
        """
        Search memories with various filters.

        Args:
            query: Search query
            memory_types: Types of memories to search
            tags: Filter by tags
            conversation_id: Filter by conversation
            user_id: Filter by user
            limit: Maximum results
            include_content: Whether to include content in search

        Returns:
            List of search results with relevance scores
        """
        if memory_types is None:
            memory_types = list(MemoryType)

        candidates = []

        # Collect candidate memories
        for memory_type in memory_types:
            for memory in self.memories[memory_type]:
                # Apply filters
                if tags and not any(tag in memory.tags for tag in tags):
                    continue
                if conversation_id and memory.conversation_id != conversation_id:
                    continue
                if user_id and memory.user_id != user_id:
                    continue

                candidates.append(memory)

        # Calculate relevance scores
        results = []
        for memory in candidates:
            score, reasons = await self._calculate_relevance(
                memory, query, include_content
            )
            if score >= self.config.similarity_threshold:
                results.append(
                    MemorySearchResult(
                        memory_item=memory, relevance_score=score, match_reasons=reasons
                    )
                )

        # Sort by relevance score and limit results
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:limit]

    async def get_context_memories(
        self,
        conversation_id: str | None = None,
        max_tokens: int | None = None,
        memory_types: list[MemoryType] | None = None,
    ) -> list[MemoryItem]:
        """
        Get memories optimized for context inclusion.

        Args:
            conversation_id: Associated conversation
            max_tokens: Maximum tokens to include
            memory_types: Types of memories to include

        Returns:
            List of memories for context
        """
        if memory_types is None:
            memory_types = [MemoryType.SHORT_TERM, MemoryType.WORKING]

        candidates = []

        for memory_type in memory_types:
            for memory in self.memories[memory_type]:
                # Filter by conversation if specified
                if conversation_id and memory.conversation_id != conversation_id:
                    if memory_type != MemoryType.SEMANTIC:  # Include semantic memories
                        continue

                # Skip expired memories
                if memory.expires_at and memory.expires_at < datetime.now(timezone.utc):
                    continue

                candidates.append(memory)

        # Sort by priority and recency
        candidates.sort(key=lambda m: self._get_context_score(m), reverse=True)

        # Apply token limit if specified
        if max_tokens:
            selected = []
            current_tokens = 0

            for memory in candidates:
                # Simple token estimation (rough approximation)
                memory_tokens = (
                    len(memory.content.split()) * 1.3
                )  # Average token-to-word ratio

                if current_tokens + memory_tokens <= max_tokens:
                    selected.append(memory)
                    current_tokens += memory_tokens
                else:
                    break

            return selected

        return candidates[: self.config.max_context_items]

    async def cleanup_expired_memories(self) -> int:
        """Clean up expired memories and enforce size limits."""
        cleaned_count = 0
        now = datetime.now(timezone.utc)

        for memory_type, memory_list in self.memories.items():
            # Remove expired memories
            expired_indices = []
            for i, memory in enumerate(memory_list):
                if memory.expires_at and memory.expires_at < now:
                    expired_indices.append(i)

            # Remove expired memories (reverse order to maintain indices)
            for i in reversed(expired_indices):
                memory = memory_list[i]
                del memory_list[i]
                self._remove_from_indexes(memory)
                cleaned_count += 1

                if self.storage_path:
                    await self._delete_memory_storage(memory.id)

            # Enforce size limits
            await self._enforce_size_limits(memory_type)

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} expired memories")

        return cleaned_count

    async def get_memory_stats(self) -> dict[str, Any]:
        """Get statistics about memory usage."""
        stats = {
            "total_memories": 0,
            "by_type": {},
            "by_priority": {},
            "expired_count": 0,
            "average_access_count": 0,
            "oldest_memory": None,
            "newest_memory": None,
        }

        now = datetime.now(timezone.utc)
        all_memories = []
        total_access = 0

        for memory_type, memory_list in self.memories.items():
            stats["by_type"][memory_type.value] = len(memory_list)
            stats["total_memories"] += len(memory_list)

            for memory in memory_list:
                all_memories.append(memory)
                total_access += memory.access_count

                # Count by priority
                priority = memory.priority.value
                stats["by_priority"][priority] = (
                    stats["by_priority"].get(priority, 0) + 1
                )

                # Count expired
                if memory.expires_at and memory.expires_at < now:
                    stats["expired_count"] += 1

        if all_memories:
            stats["average_access_count"] = total_access / len(all_memories)
            stats["oldest_memory"] = min(
                all_memories, key=lambda m: m.created_at
            ).created_at.isoformat()
            stats["newest_memory"] = max(
                all_memories, key=lambda m: m.created_at
            ).created_at.isoformat()

        return stats

    def _update_indexes(self, memory: MemoryItem) -> None:
        """Update search indexes for a memory item."""
        # Tag index
        for tag in memory.tags:
            if tag not in self.indexes["tags"]:
                self.indexes["tags"][tag] = []
            if memory.id not in self.indexes["tags"][tag]:
                self.indexes["tags"][tag].append(memory.id)

        # Conversation index
        if memory.conversation_id:
            if memory.conversation_id not in self.indexes["conversation_id"]:
                self.indexes["conversation_id"][memory.conversation_id] = []
            if memory.id not in self.indexes["conversation_id"][memory.conversation_id]:
                self.indexes["conversation_id"][memory.conversation_id].append(
                    memory.id
                )

        # User index
        if memory.user_id:
            if memory.user_id not in self.indexes["user_id"]:
                self.indexes["user_id"][memory.user_id] = []
            if memory.id not in self.indexes["user_id"][memory.user_id]:
                self.indexes["user_id"][memory.user_id].append(memory.id)

        # Content hash index (for deduplication)
        content_hash = hashlib.md5(memory.content.encode()).hexdigest()
        if content_hash not in self.indexes["content_hash"]:
            self.indexes["content_hash"][content_hash] = []
        if memory.id not in self.indexes["content_hash"][content_hash]:
            self.indexes["content_hash"][content_hash].append(memory.id)

    def _remove_from_indexes(self, memory: MemoryItem) -> None:
        """Remove a memory item from all indexes."""
        # Remove from tag index
        for tag in memory.tags:
            if tag in self.indexes["tags"] and memory.id in self.indexes["tags"][tag]:
                self.indexes["tags"][tag].remove(memory.id)
                if not self.indexes["tags"][tag]:
                    del self.indexes["tags"][tag]

        # Remove from conversation index
        if memory.conversation_id:
            if (
                memory.conversation_id in self.indexes["conversation_id"]
                and memory.id in self.indexes["conversation_id"][memory.conversation_id]
            ):
                self.indexes["conversation_id"][memory.conversation_id].remove(
                    memory.id
                )
                if not self.indexes["conversation_id"][memory.conversation_id]:
                    del self.indexes["conversation_id"][memory.conversation_id]

        # Remove from user index
        if memory.user_id:
            if (
                memory.user_id in self.indexes["user_id"]
                and memory.id in self.indexes["user_id"][memory.user_id]
            ):
                self.indexes["user_id"][memory.user_id].remove(memory.id)
                if not self.indexes["user_id"][memory.user_id]:
                    del self.indexes["user_id"][memory.user_id]

        # Remove from content hash index
        content_hash = hashlib.md5(memory.content.encode()).hexdigest()
        if (
            content_hash in self.indexes["content_hash"]
            and memory.id in self.indexes["content_hash"][content_hash]
        ):
            self.indexes["content_hash"][content_hash].remove(memory.id)
            if not self.indexes["content_hash"][content_hash]:
                del self.indexes["content_hash"][content_hash]

    async def _calculate_relevance(
        self, memory: MemoryItem, query: str, include_content: bool
    ) -> tuple[float, list[str]]:
        """Calculate relevance score for a memory item."""
        score = 0.0
        reasons = []

        # Content similarity (if enabled)
        if include_content and self.config.enable_semantic_search and memory.embedding:
            # This would use actual embedding similarity in a real implementation
            # For now, we'll use simple text matching
            query_lower = query.lower()
            content_lower = memory.content.lower()

            if query_lower in content_lower:
                score += 0.8
                reasons.append("Exact content match")
            elif any(word in content_lower for word in query_lower.split()):
                score += 0.5
                reasons.append("Partial content match")

        # Tag matching
        query_lower = query.lower()
        for tag in memory.tags:
            if query_lower in tag.lower() or tag.lower() in query_lower:
                score += 0.3
                reasons.append(f"Tag match: {tag}")

        # Priority bonus
        priority_scores = {
            MemoryPriority.LOW: 0.1,
            MemoryPriority.MEDIUM: 0.2,
            MemoryPriority.HIGH: 0.3,
            MemoryPriority.CRITICAL: 0.4,
        }
        score += priority_scores[memory.priority]
        reasons.append(f"Priority: {memory.priority.value}")

        # Recency bonus (if configured)
        if self.config.prioritize_recent:
            days_old = (datetime.now(timezone.utc) - memory.created_at).days
            recency_bonus = max(0, 0.2 - (days_old * 0.01))
            score += recency_bonus
            if recency_bonus > 0:
                reasons.append("Recent memory")

        # Access frequency bonus (if configured)
        if self.config.prioritize_accessed and memory.access_count > 0:
            access_bonus = min(0.2, memory.access_count * 0.02)
            score += access_bonus
            reasons.append("Frequently accessed")

        return min(score, 1.0), reasons

    def _get_context_score(self, memory: MemoryItem) -> float:
        """Get context optimization score for a memory."""
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

    async def _enforce_size_limits(self, memory_type: MemoryType) -> None:
        """Enforce size limits for a memory type."""
        memory_list = self.memories[memory_type]

        # Define limits by type
        limits = {
            MemoryType.SHORT_TERM: self.config.max_short_term_items,
            MemoryType.LONG_TERM: self.config.max_long_term_items,
            MemoryType.EPISODIC: self.config.max_long_term_items,
            MemoryType.SEMANTIC: self.config.max_long_term_items,
            MemoryType.WORKING: 100,  # Working memory is smaller
        }

        limit = limits.get(memory_type, self.config.max_short_term_items)

        if len(memory_list) > limit:
            # Sort by context score (lowest first) and remove excess
            memory_list.sort(key=lambda m: self._get_context_score(m))
            excess_count = len(memory_list) - limit

            for i in range(excess_count):
                memory = memory_list[i]
                memory_list.remove(memory)
                self._remove_from_indexes(memory)

                if self.storage_path:
                    await self._delete_memory_storage(memory.id)

    async def _generate_embedding(self, memory: MemoryItem) -> None:
        """Generate embedding for semantic search."""
        # This would use an actual embedding model in a real implementation
        # For now, we'll create a dummy embedding
        try:
            # Placeholder for actual embedding generation
            # import openai
            # response = await openai.Embedding.acreate(
            #     model=self.config.embedding_model,
            #     input=memory.content
            # )
            # memory.embedding = response['data'][0]['embedding']

            # Dummy embedding for now
            memory.embedding = [0.0] * 1536  # OpenAI embeddings are 1536 dimensions

        except Exception as e:
            logger.error(f"Error generating embedding for memory {memory.id}: {e}")

    def _start_cleanup_task(self) -> None:
        """Start the periodic cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self) -> None:
        """Periodic cleanup loop."""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval_hours * 3600)
                await self.cleanup_expired_memories()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _save_memory(self, memory: MemoryItem) -> None:
        """Save a memory item to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)
        memory_file = self.storage_path / f"{memory.id}.json"

        with open(memory_file, "w") as f:
            json.dump(memory.to_dict(), f, indent=2)

    async def _delete_memory_storage(self, memory_id: str) -> None:
        """Delete a memory item from storage."""
        if not self.storage_path:
            return

        memory_file = self.storage_path / f"{memory_id}.json"
        if memory_file.exists():
            memory_file.unlink()

    def _load_memories(self) -> None:
        """Load memories from storage."""
        if not self.storage_path or not self.storage_path.exists():
            return

        loaded_count = 0
        for memory_file in self.storage_path.glob("*.json"):
            try:
                with open(memory_file) as f:
                    data = json.load(f)

                memory = MemoryItem.from_dict(data)
                self.memories[memory.memory_type].append(memory)
                self._update_indexes(memory)
                loaded_count += 1

            except Exception as e:
                logger.error(f"Error loading memory from {memory_file}: {e}")

        logger.info(f"Loaded {loaded_count} memories from storage")

    async def shutdown(self) -> None:
        """Shutdown the memory manager."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
