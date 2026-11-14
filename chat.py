from openai import OpenAI

from models import Conversation, Message
from repository import ConversationRepository


class ChatService:
    """Sends messages to the model and stores each exchange."""

    def __init__(
        self,
        client: OpenAI,
        repository: ConversationRepository,
        model: str,
        instructions: str,
        conversation: Conversation | None = None,
    ):
        self.client = client
        self.repository = repository
        self.model = model
        self.instructions = instructions
        self.conversation = conversation or Conversation()

    def send(self, user_input: str) -> str:
        """Sends the user input and returns the model's reply."""
        if self.conversation.id is None:
            self.conversation.id = self.repository.create_conversation()

        response = self.client.responses.create(
            model=self.model,
            instructions=self.instructions,
            input=user_input,
            previous_response_id=self.conversation.last_response_id,
        )

        message = Message(
            user_prompt=user_input,
            system_prompt=self.instructions,
            output_text=response.output_text,
        )
        self.conversation.last_response_id = response.id
        self.repository.add_message(self.conversation.id, message, response.id)
        return response.output_text
