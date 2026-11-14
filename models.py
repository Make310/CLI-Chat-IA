from pydantic import BaseModel


class Message(BaseModel):
    user_prompt: str
    system_prompt: str
    output_text: str = ""


class Conversation(BaseModel):
    id: int | None = None  # None until saved to the database
    last_response_id: str | None = None
