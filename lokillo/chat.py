from collections.abc import Iterator

from openai import OpenAI

from lokillo.models import Conversation, Message
from lokillo.repository import ConversationRepository

TEXT_DELTA_EVENT = "response.output_text.delta"


class ChatService:
    """Sends messages to the model and stores each exchange."""

    def __init__(
        self,
        client: OpenAI,
        repository: ConversationRepository,
        model: str,
        instructions: str,
        temperature: float | None = None,
        conversation: Conversation | None = None,
    ):
        self.client = client
        self.repository = repository
        self.model = model
        self.instructions = instructions
        self.temperature = temperature
        self.conversation = conversation or Conversation()

    def send(self, user_input: str) -> Iterator[str]:
        """Streams the reply chunk by chunk and saves it once complete."""
        if self.conversation.id is None:
            self.conversation.id = self.repository.create_conversation()

        stream = self.client.responses.create(
            model=self.model,
            instructions=self.instructions,
            input=self._build_input(user_input),
            stream=True,
            **self._optional_params(),
        )

        chunks = []
        for event in stream:
            if event.type == TEXT_DELTA_EVENT:
                chunks.append(event.delta)
                yield event.delta

        message = Message(
            user_prompt=user_input,
            system_prompt=self.instructions,
            output_text="".join(chunks),
        )
        self.repository.add_message(self.conversation.id, message)
        self.conversation.messages.append(message)

    def _optional_params(self) -> dict[str, float]:
        """Only sends parameters that were set, so model defaults apply."""
        if self.temperature is None:
            return {}
        return {"temperature": self.temperature}

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
