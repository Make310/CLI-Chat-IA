import sqlite3
from pathlib import Path

from models import Message

SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    last_response_id TEXT,
    created_at       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_prompt     TEXT NOT NULL,
    system_prompt   TEXT NOT NULL,
    output_text     TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
"""


class ConversationRepository:
    """Persists conversations and messages in SQLite."""

    def __init__(self, db_path: str | Path = "conversations.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)

    def create_conversation(self) -> int:
        with self.conn:
            return self.conn.execute("INSERT INTO conversations DEFAULT VALUES").lastrowid

    def add_message(self, conversation_id: int, message: Message, last_response_id: str) -> None:
        """Inserts the message and updates the conversation in a single transaction."""
        with self.conn:
            self.conn.execute(
                "INSERT INTO messages (conversation_id, user_prompt, system_prompt, output_text) "
                "VALUES (?, ?, ?, ?)",
                (conversation_id, message.user_prompt, message.system_prompt, message.output_text),
            )
            self.conn.execute(
                "UPDATE conversations SET last_response_id = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE id = ?",
                (last_response_id, conversation_id),
            )

    def close(self) -> None:
        self.conn.close()
