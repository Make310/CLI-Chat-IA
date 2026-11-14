from openai import OpenAI

from lokillo.models import Conversation, Message
from lokillo.repository import ConversationRepository


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
        """Sends the user input with the full history and returns the reply."""
        if self.conversation.id is None:
            self.conversation.id = self.repository.create_conversation()

        response = self.client.responses.create(
            model=self.model,
            instructions=self.instructions,
            input=self._build_input(user_input),
        )

        message = Message(
            user_prompt=user_input,
            system_prompt=self.instructions,
            output_text=response.output_text,
        )
        self.repository.add_message(self.conversation.id, message)
        self.conversation.messages.append(message)
        return response.output_text

    def _build_input(self, user_input: str) -> list[dict[str, str]]:
        """Builds the user/assistant history followed by the new prompt."""
        history = []
        for message in self.conversation.messages:
            history.append({"role": "user", "content": message.user_prompt})
            history.append(
                {"role": "assistant", "content": message.output_text}
            )
        history.append({"role": "user", "content": user_input})
        return history
