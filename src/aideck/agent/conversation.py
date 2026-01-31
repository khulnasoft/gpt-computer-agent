"""
Conversation Management System for GPT Agents

This module provides comprehensive conversation management capabilities including
message handling, context management, conversation history, and state persistence.
"""

import json
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Enumeration of possible message roles."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"


class MessageStatus(str, Enum):
    """Enumeration of message statuses."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ConversationMetadata:
    """Metadata for a conversation."""

    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: list[str] = field(default_factory=list)
    user_id: str | None = None
    session_id: str | None = None
    model_name: str | None = None
    total_messages: int = 0
    total_tokens: int = 0


class ConversationMessage(BaseModel):
    """Represents a single message in a conversation."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    role: MessageRole
    content: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    name: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: MessageStatus = MessageStatus.COMPLETED
    metadata: dict[str, Any] = Field(default_factory=dict)
    token_count: int | None = None
    parent_id: str | None = None  # For message threading
    children_ids: list[str] = Field(default_factory=list)  # For message threading

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ConversationContext(BaseModel):
    """Context information for a conversation."""

    conversation_id: str
    current_turn: int = 0
    max_context_length: int = 10000  # Maximum tokens in context
    include_system_messages: bool = True
    include_tool_messages: bool = True
    context_window: int = 10  # Number of recent messages to include
    summary: str | None = None  # Conversation summary for long conversations
    key_points: list[str] = Field(default_factory=list)  # Key points from conversation

    def to_dict(self) -> dict[str, Any]:
        """Convert context to dictionary."""
        return self.dict()


class ConversationManager:
    """
    Manages conversations for GPT agents with advanced features like
    context management, history tracking, and state persistence.
    """

    def __init__(self, storage_path: str | Path | None = None):
        self.storage_path = Path(storage_path) if storage_path else None
        self.conversations: dict[str, list[ConversationMessage]] = {}
        self.metadata: dict[str, ConversationMetadata] = {}
        self.contexts: dict[str, ConversationContext] = {}
        self.active_conversation: str | None = None

        # Load existing conversations if storage path is provided
        if self.storage_path:
            self._load_conversations()

    def create_conversation(
        self,
        title: str | None = None,
        system_prompt: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        model_name: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """
        Create a new conversation.

        Args:
            title: Optional title for the conversation
            system_prompt: Optional system prompt to start the conversation
            user_id: Optional user identifier
            session_id: Optional session identifier
            model_name: Optional model name being used
            tags: Optional tags for the conversation

        Returns:
            The conversation ID
        """
        conversation_id = str(uuid.uuid4())

        # Create metadata
        metadata = ConversationMetadata(
            conversation_id=conversation_id,
            title=title or f"Conversation {conversation_id[:8]}",
            user_id=user_id,
            session_id=session_id,
            model_name=model_name,
            tags=tags or [],
        )

        # Initialize conversation and context
        self.conversations[conversation_id] = []
        self.metadata[conversation_id] = metadata
        self.contexts[conversation_id] = ConversationContext(
            conversation_id=conversation_id
        )

        # Add system prompt if provided
        if system_prompt:
            self.add_message(
                conversation_id=conversation_id,
                role=MessageRole.SYSTEM,
                content=system_prompt,
            )

        # Set as active conversation
        self.active_conversation = conversation_id

        logger.info(f"Created new conversation: {conversation_id}")
        return conversation_id

    def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str | None = None,
        tool_calls: list[dict[str, Any]] | None = None,
        tool_call_id: str | None = None,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
        parent_id: str | None = None,
    ) -> ConversationMessage:
        """
        Add a message to a conversation.

        Args:
            conversation_id: ID of the conversation
            role: Role of the message sender
            content: Content of the message
            tool_calls: Tool calls made by the assistant
            tool_call_id: ID of the tool call this message responds to
            name: Name of the tool that was called
            metadata: Additional metadata for the message
            parent_id: Parent message ID for threading

        Returns:
            The created message
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            tool_call_id=tool_call_id,
            name=name,
            metadata=metadata or {},
            parent_id=parent_id,
        )

        # Add to conversation
        self.conversations[conversation_id].append(message)

        # Update metadata
        if conversation_id in self.metadata:
            self.metadata[conversation_id].total_messages += 1
            self.metadata[conversation_id].updated_at = datetime.now(timezone.utc)

        # Update context
        if conversation_id in self.contexts:
            self.contexts[conversation_id].current_turn += 1

        # Handle threading
        if parent_id and parent_id in [
            msg.id for msg in self.conversations[conversation_id]
        ]:
            for msg in self.conversations[conversation_id]:
                if msg.id == parent_id:
                    msg.children_ids.append(message.id)
                    break

        # Save if storage path is provided
        if self.storage_path:
            self._save_conversation(conversation_id)

        logger.debug(f"Added message to conversation {conversation_id}: {role.value}")
        return message

    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int | None = None,
        include_system: bool = True,
        include_tools: bool = True,
    ) -> list[ConversationMessage]:
        """
        Get messages from a conversation.

        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return
            include_system: Whether to include system messages
            include_tools: Whether to include tool messages

        Returns:
            List of messages
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        messages = self.conversations[conversation_id]

        # Filter messages
        filtered_messages = []
        for message in messages:
            if not include_system and message.role == MessageRole.SYSTEM:
                continue
            if not include_tools and message.role == MessageRole.TOOL:
                continue
            filtered_messages.append(message)

        # Apply limit
        if limit:
            filtered_messages = filtered_messages[-limit:]

        return filtered_messages

    def get_context_messages(
        self, conversation_id: str, max_tokens: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Get messages formatted for LLM context with smart truncation.

        Args:
            conversation_id: ID of the conversation
            max_tokens: Maximum tokens to include in context

        Returns:
            List of messages in OpenAI format
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        context = self.contexts.get(conversation_id)
        if not context:
            context = ConversationContext(conversation_id=conversation_id)
            self.contexts[conversation_id] = context

        messages = self.get_conversation_messages(
            conversation_id,
            include_system=context.include_system_messages,
            include_tools=context.include_tool_messages,
        )

        # Convert to OpenAI format
        openai_messages = []
        for message in messages:
            msg_dict = {"role": message.role.value, "content": message.content}

            if message.tool_calls:
                msg_dict["tool_calls"] = message.tool_calls

            if message.tool_call_id:
                msg_dict["tool_call_id"] = message.tool_call_id

            if message.name:
                msg_dict["name"] = message.name

            openai_messages.append(msg_dict)

        # Apply context window and token limits
        if context.context_window and len(openai_messages) > context.context_window:
            # Keep system messages and recent messages
            system_messages = [
                msg for msg in openai_messages if msg["role"] == "system"
            ]
            other_messages = [msg for msg in openai_messages if msg["role"] != "system"]
            other_messages = other_messages[-context.context_window :]
            openai_messages = system_messages + other_messages

        return openai_messages

    def update_conversation_title(self, conversation_id: str, title: str) -> None:
        """Update the title of a conversation."""
        if conversation_id in self.metadata:
            self.metadata[conversation_id].title = title
            self.metadata[conversation_id].updated_at = datetime.now(timezone.utc)

            if self.storage_path:
                self._save_conversation(conversation_id)

    def add_tag(self, conversation_id: str, tag: str) -> None:
        """Add a tag to a conversation."""
        if conversation_id in self.metadata:
            if tag not in self.metadata[conversation_id].tags:
                self.metadata[conversation_id].tags.append(tag)
                self.metadata[conversation_id].updated_at = datetime.now(timezone.utc)

                if self.storage_path:
                    self._save_conversation(conversation_id)

    def remove_tag(self, conversation_id: str, tag: str) -> None:
        """Remove a tag from a conversation."""
        if conversation_id in self.metadata:
            if tag in self.metadata[conversation_id].tags:
                self.metadata[conversation_id].tags.remove(tag)
                self.metadata[conversation_id].updated_at = datetime.now(timezone.utc)

                if self.storage_path:
                    self._save_conversation(conversation_id)

    def list_conversations(
        self,
        user_id: str | None = None,
        tags: list[str] | None = None,
        limit: int | None = None,
    ) -> list[ConversationMetadata]:
        """
        List conversations with optional filtering.

        Args:
            user_id: Filter by user ID
            tags: Filter by tags (must match all tags)
            limit: Maximum number of conversations to return

        Returns:
            List of conversation metadata
        """
        conversations = list(self.metadata.values())

        # Apply filters
        if user_id:
            conversations = [c for c in conversations if c.user_id == user_id]

        if tags:
            conversations = [
                c for c in conversations if all(tag in c.tags for tag in tags)
            ]

        # Sort by updated_at (most recent first)
        conversations.sort(key=lambda c: c.updated_at, reverse=True)

        # Apply limit
        if limit:
            conversations = conversations[:limit]

        return conversations

    def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
        if conversation_id in self.metadata:
            del self.metadata[conversation_id]
        if conversation_id in self.contexts:
            del self.contexts[conversation_id]

        if self.active_conversation == conversation_id:
            self.active_conversation = None

        # Delete from storage
        if self.storage_path:
            storage_file = self.storage_path / f"{conversation_id}.json"
            if storage_file.exists():
                storage_file.unlink()

        logger.info(f"Deleted conversation: {conversation_id}")

    def set_active_conversation(self, conversation_id: str) -> None:
        """Set the active conversation."""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        self.active_conversation = conversation_id

    def get_active_conversation(self) -> str | None:
        """Get the active conversation ID."""
        return self.active_conversation

    def get_conversation_stats(self, conversation_id: str) -> dict[str, Any]:
        """Get statistics for a conversation."""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        messages = self.conversations[conversation_id]
        metadata = self.metadata[conversation_id]

        # Count messages by role
        role_counts = {}
        for message in messages:
            role_counts[message.role.value] = role_counts.get(message.role.value, 0) + 1

        return {
            "conversation_id": conversation_id,
            "title": metadata.title,
            "total_messages": len(messages),
            "role_counts": role_counts,
            "created_at": metadata.created_at.isoformat(),
            "updated_at": metadata.updated_at.isoformat(),
            "tags": metadata.tags,
            "current_turn": self.contexts.get(
                conversation_id, ConversationContext(conversation_id=conversation_id)
            ).current_turn,
        }

    async def stream_conversation(
        self, conversation_id: str, message_generator: AsyncGenerator[str, None]
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response to a conversation.

        Args:
            conversation_id: ID of the conversation
            message_generator: Async generator yielding message chunks

        Yields:
            Message chunks
        """
        # Create a placeholder message for the streaming response
        placeholder_message = ConversationMessage(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="",
            status=MessageStatus.PROCESSING,
        )

        self.conversations[conversation_id].append(placeholder_message)

        try:
            # Stream the response
            content_parts = []
            async for chunk in message_generator:
                content_parts.append(chunk)
                yield chunk

            # Update the placeholder message with the complete content
            placeholder_message.content = "".join(content_parts)
            placeholder_message.status = MessageStatus.COMPLETED

        except Exception as e:
            placeholder_message.status = MessageStatus.FAILED
            placeholder_message.metadata["error"] = str(e)
            logger.error(f"Error streaming to conversation {conversation_id}: {e}")
            raise

        finally:
            # Save the conversation
            if self.storage_path:
                self._save_conversation(conversation_id)

    def _save_conversation(self, conversation_id: str) -> None:
        """Save a conversation to storage."""
        if not self.storage_path:
            return

        self.storage_path.mkdir(parents=True, exist_ok=True)

        conversation_data = {
            "metadata": self.metadata[conversation_id].__dict__,
            "messages": [
                message.dict() for message in self.conversations[conversation_id]
            ],
            "context": self.contexts[conversation_id].dict(),
        }

        storage_file = self.storage_path / f"{conversation_id}.json"
        with open(storage_file, "w") as f:
            json.dump(conversation_data, f, indent=2, default=str)

    def _load_conversations(self) -> None:
        """Load conversations from storage."""
        if not self.storage_path or not self.storage_path.exists():
            return

        for storage_file in self.storage_path.glob("*.json"):
            try:
                with open(storage_file) as f:
                    conversation_data = json.load(f)

                conversation_id = storage_file.stem

                # Load metadata
                metadata_dict = conversation_data["metadata"]
                metadata = ConversationMetadata(**metadata_dict)

                # Load messages
                messages = []
                for message_dict in conversation_data["messages"]:
                    message = ConversationMessage(**message_dict)
                    messages.append(message)

                # Load context
                context = ConversationContext(**conversation_data["context"])

                # Store in memory
                self.conversations[conversation_id] = messages
                self.metadata[conversation_id] = metadata
                self.contexts[conversation_id] = context

            except Exception as e:
                logger.error(f"Error loading conversation from {storage_file}: {e}")

        logger.info(f"Loaded {len(self.conversations)} conversations from storage")
