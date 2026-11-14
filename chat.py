from openai import OpenAI

from models import Conversation, Message
from repository import ConversationRepository


class ChatService:
    def __init__(self, client: OpenAI, repository: ConversationRepository, model: str, instructions: str):
        self.client = client
        self.repository = repository
        self.model = model
        self.instructions = instructions
        self.conversation = Conversation()

    def send(self, user_input: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=self.instructions,
            input=user_input,
            previous_response_id=self.conversation.conversation_id,
        )
        self.conversation.conversation_id = response.id
        self.conversation.add_message(
            Message(user_prompt=user_input, system_prompt=self.instructions, output_text=response.output_text)
        )
        self.repository.save(self.conversation)
        return response.output_text
