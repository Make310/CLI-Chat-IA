import sqlite3
from contextlib import closing
from pathlib import Path

from models import Conversation

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
        self.db_path = Path(db_path)
        with closing(self._connect()) as conn:
            conn.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def save(self, conversation: Conversation) -> None:
        """Creates or updates the conversation and inserts only new messages."""
        with closing(self._connect()) as conn, conn:
            if conversation.id is None:
                cur = conn.execute(
                    "INSERT INTO conversations (last_response_id) VALUES (?)",
                    (conversation.conversation_id,),
                )
                conversation.id = cur.lastrowid
            else:
                conn.execute(
                    "UPDATE conversations SET last_response_id = ?, "
                    "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (conversation.conversation_id, conversation.id),
                )

            for message in conversation.messages:
                if message.id is not None:
                    continue
                cur = conn.execute(
                    "INSERT INTO messages (conversation_id, user_prompt, system_prompt, output_text) "
                    "VALUES (?, ?, ?, ?)",
                    (conversation.id, message.user_prompt, message.system_prompt, message.output_text),
                )
                message.id = cur.lastrowid
