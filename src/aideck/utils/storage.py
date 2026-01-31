""
Persistent storage for conversation history and agent state.
"""
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
import sqlite3
from datetime import datetime
import uuid

from loguru import logger
from pydantic import BaseModel, Field

class Message(BaseModel):
    """A message in a conversation."""
    role: str  # 'user', 'agent', 'system', or 'tool'
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Conversation(BaseModel):
    """A conversation between the user and the agent."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Conversation"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[Message] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Storage:
    """Persistent storage for conversations and agent state."""

    def __init__(self, db_path: Union[str, Path] = "gpt_agent.db"):
        """Initialize the storage.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    metadata TEXT NOT NULL
                )
            """)

            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    metadata TEXT NOT NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
                ON messages (conversation_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_updated_at
                ON conversations (updated_at)
            """)

            conn.commit()

    def create_conversation(self, title: str = "New Conversation") -> str:
        """Create a new conversation.

        Args:
            title: Title for the new conversation.

        Returns:
            The ID of the created conversation.
        """
        conversation = Conversation(title=title)
        self._save_conversation(conversation)
        return conversation.id

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID.

        Args:
            conversation_id: ID of the conversation to retrieve.

        Returns:
            The conversation, or None if not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get conversation
            cursor.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conversation_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            # Get messages
            cursor.execute(
                """
                SELECT role, content, timestamp, metadata
                FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
                """,
                (conversation_id,)
            )

            messages = []
            for msg_row in cursor.fetchall():
                messages.append(Message(
                    role=msg_row['role'],
                    content=msg_row['content'],
                    timestamp=datetime.fromisoformat(msg_row['timestamp']),
                    metadata=json.loads(msg_row['metadata'])
                ))

            return Conversation(
                id=row['id'],
                title=row['title'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                messages=messages,
                metadata=json.loads(row['metadata'])
            )

    def list_conversations(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """List recent conversations.

        Args:
            limit: Maximum number of conversations to return.
            offset: Number of conversations to skip.

        Returns:
            List of conversations with basic information.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, title, created_at, updated_at
                FROM conversations
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            )

            return [dict(row) for row in cursor.fetchall()]

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a message to a conversation.

        Args:
            conversation_id: ID of the conversation.
            role: Role of the message sender ('user', 'agent', 'system', or 'tool').
            content: Content of the message.
            metadata: Additional metadata for the message.
        """
        if metadata is None:
            metadata = {}

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if conversation exists
            cursor.execute(
                "SELECT id FROM conversations WHERE id = ?",
                (conversation_id,)
            )
            if not cursor.fetchone():
                raise ValueError(f"Conversation {conversation_id} not found")

            # Insert message
            cursor.execute(
                """
                INSERT INTO messages
                (conversation_id, role, content, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    role,
                    content,
                    datetime.utcnow().isoformat(),
                    json.dumps(metadata)
                )
            )

            # Update conversation's updated_at
            cursor.execute(
                """
                UPDATE conversations
                SET updated_at = ?
                WHERE id = ?
                """,
                (datetime.utcnow().isoformat(), conversation_id)
            )

            conn.commit()

    def _save_conversation(self, conversation: Conversation) -> None:
        """Save a conversation to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Insert or update conversation
            cursor.execute(
                """
                INSERT OR REPLACE INTO conversations
                (id, title, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    conversation.id,
                    conversation.title,
                    conversation.created_at.isoformat(),
                    conversation.updated_at.isoformat(),
                    json.dumps(conversation.metadata)
                )
            )

            # Delete existing messages
            cursor.execute(
                "DELETE FROM messages WHERE conversation_id = ?",
                (conversation.id,)
            )

            # Insert messages
            for msg in conversation.messages:
                cursor.execute(
                    """
                    INSERT INTO messages
                    (conversation_id, role, content, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        conversation.id,
                        msg.role,
                        msg.content,
                        msg.timestamp.isoformat(),
                        json.dumps(msg.metadata)
                    )
                )

            conn.commit()

    def delete_conversation(self, conversation_id: str) -> None:
        """Delete a conversation and all its messages.

        Args:
            conversation_id: ID of the conversation to delete.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Delete messages
            cursor.execute(
                "DELETE FROM messages WHERE conversation_id = ?",
                (conversation_id,)
            )

            # Delete conversation
            cursor.execute(
                "DELETE FROM conversations WHERE id = ?",
                (conversation_id,)
            )

            conn.commit()

# Singleton instance
storage = Storage()
