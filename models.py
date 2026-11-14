import json
from pathlib import Path

from pydantic import BaseModel, Field, PrivateAttr

CONVERSATIONS_FILE = Path("conversations.json")


class Message(BaseModel):
    user_prompt: str
    system_prompt: str
    output_text: str = ""


class Conversation(BaseModel):
    _key: str | None = PrivateAttr(default=None)
    conversation_id: str | None = None
    messages: list[Message] = Field(default_factory=list)

    def add_message(self, message: Message) -> None:
        self.messages.append(message)

    def save(self) -> None:
        data = {}
        if CONVERSATIONS_FILE.exists():
            with open(CONVERSATIONS_FILE, encoding="utf-8") as f:
                content = f.read().strip()
                data = json.loads(content) if content else {}

        if self._key is None:
            self._key = str(max((int(k) for k in data), default=0) + 1)

        data[self._key] = self.model_dump(mode="json")

        with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
