from pydantic import BaseModel, Field


class Message(BaseModel):
    user_prompt: str
    system_prompt: str
    output_text: str = ""


class Conversation(BaseModel):
    id: int | None = None  # None until saved to the database
    messages: list[Message] = Field(default_factory=list)


class ConversationSummary(BaseModel):
    id: int
    updated_at: str
    first_prompt: str
    message_count: int
