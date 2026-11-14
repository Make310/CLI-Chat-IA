import sqlite3
from pathlib import Path

from lokillo.models import Conversation, ConversationSummary, Message

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "conversations.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL
                    REFERENCES conversations(id) ON DELETE CASCADE,
    user_prompt     TEXT NOT NULL,
    system_prompt   TEXT NOT NULL,
    output_text     TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation
    ON messages(conversation_id);
"""

INSERT_CONVERSATION = "INSERT INTO conversations DEFAULT VALUES"

INSERT_MESSAGE = """
INSERT INTO messages (conversation_id, user_prompt, system_prompt, output_text)
VALUES (:conversation_id, :user_prompt, :system_prompt, :output_text)
"""

TOUCH_CONVERSATION = """
UPDATE conversations
SET updated_at = CURRENT_TIMESTAMP
WHERE id = :conversation_id
"""

SELECT_CONVERSATION = """
SELECT id
FROM conversations
WHERE id = :conversation_id
"""

SELECT_MESSAGES = """
SELECT user_prompt, system_prompt, output_text
FROM messages
WHERE conversation_id = :conversation_id
ORDER BY id
"""

SELECT_RECENT_CONVERSATIONS = """
SELECT
    conversation.id,
    conversation.updated_at,
    first_message.user_prompt AS first_prompt,
    COUNT(message.id) AS message_count
FROM conversations AS conversation
JOIN messages AS message
    ON message.conversation_id = conversation.id
JOIN messages AS first_message
    ON first_message.id = (
        SELECT MIN(id) FROM messages WHERE conversation_id = conversation.id
    )
GROUP BY conversation.id
ORDER BY MAX(message.id) DESC
LIMIT :limit
"""


class ConversationRepository:
    """Persists conversations and messages in SQLite."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(SCHEMA)

    def create_conversation(self) -> int:
        """Creates an empty conversation and returns its ID."""
        with self.connection:
            cursor = self.connection.execute(INSERT_CONVERSATION)
        return cursor.lastrowid

    def add_message(self, conversation_id: int, message: Message) -> None:
        """Saves the message and updates the conversation atomically."""
        with self.connection:
            self.connection.execute(
                INSERT_MESSAGE,
                {"conversation_id": conversation_id, **message.model_dump()},
            )
            self.connection.execute(
                TOUCH_CONVERSATION,
                {"conversation_id": conversation_id},
            )

    def get_conversation(self, conversation_id: int) -> Conversation | None:
        """Returns the conversation with its messages, or None."""
        row = self.connection.execute(
            SELECT_CONVERSATION,
            {"conversation_id": conversation_id},
        ).fetchone()
        if row is None:
            return None
        return Conversation(
            id=row["id"],
            messages=self._get_messages(conversation_id),
        )

    def _get_messages(self, conversation_id: int) -> list[Message]:
        """Returns the conversation's messages in chronological order."""
        rows = self.connection.execute(
            SELECT_MESSAGES,
            {"conversation_id": conversation_id},
        ).fetchall()
        return [Message(**row) for row in rows]

    def list_conversations(self, limit: int = 10) -> list[ConversationSummary]:
        """Returns the most recent conversations that have messages."""
        rows = self.connection.execute(
            SELECT_RECENT_CONVERSATIONS,
            {"limit": limit},
        ).fetchall()
        return [ConversationSummary(**row) for row in rows]

    def close(self) -> None:
        """Closes the database connection."""
        self.connection.close()
