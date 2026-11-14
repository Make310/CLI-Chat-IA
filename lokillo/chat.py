from collections.abc import Iterator

from openai import OpenAI

from lokillo.models import Conversation, Message, ModelPricing
from lokillo.repository import ConversationRepository

TEXT_DELTA_EVENT = "response.output_text.delta"
COMPLETED_EVENT = "response.completed"


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
        pricing: ModelPricing | None = None,
    ):
        self.client = client
        self.repository = repository
        self.model = model
        self.instructions = instructions
        self.temperature = temperature
        self.conversation = conversation or Conversation()
        self.pricing = pricing
        self.last_message: Message | None = None

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
        usage = None
        for event in stream:
            if event.type == TEXT_DELTA_EVENT:
                chunks.append(event.delta)
                yield event.delta
            elif event.type == COMPLETED_EVENT:
                usage = event.response.usage

        message = Message(
            user_prompt=user_input,
            system_prompt=self.instructions,
            output_text="".join(chunks),
            **self._usage_fields(usage),
        )
        self.repository.add_message(self.conversation.id, message)
        self.conversation.messages.append(message)
        self.last_message = message

    def _usage_fields(self, usage) -> dict[str, int | float | None]:
        """Extracts token counts and cost from the API usage, if any."""
        if usage is None:
            return {}

        cached_tokens = 0
        if usage.input_tokens_details:
            cached_tokens = usage.input_tokens_details.cached_tokens or 0

        cost = None
        if self.pricing is not None:
            cost = float(
                self.pricing.cost(
                    usage.input_tokens, cached_tokens, usage.output_tokens
                )
            )

        return {
            "input_tokens": usage.input_tokens,
            "output_tokens": usage.output_tokens,
            "cost": cost,
        }

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
