from pydantic import BaseModel, Field


class Message(BaseModel):
    id: int | None = None  # None until saved to the database
    user_prompt: str
    system_prompt: str
    output_text: str = ""


class Conversation(BaseModel):
    id: int | None = None  # None until saved to the database
    conversation_id: str | None = None
    messages: list[Message] = Field(default_factory=list)

    def add_message(self, message: Message) -> None:
        self.messages.append(message)
