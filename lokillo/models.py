from decimal import Decimal

from pydantic import BaseModel, Field

TOKENS_PER_MILLION = Decimal(1_000_000)


class Message(BaseModel):
    user_prompt: str
    system_prompt: str
    output_text: str = ""
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost: float | None = None  # USD, None if the model's price is unknown


class Conversation(BaseModel):
    id: int | None = None  # None until saved to the database
    messages: list[Message] = Field(default_factory=list)


class ConversationSummary(BaseModel):
    id: int
    updated_at: str
    first_prompt: str
    message_count: int


class ModelPricing(BaseModel):
    """Prices in USD per million tokens."""

    input_per_million: Decimal
    cached_input_per_million: Decimal
    output_per_million: Decimal

    def cost(
        self,
        input_tokens: int,
        cached_tokens: int,
        output_tokens: int,
    ) -> Decimal:
        uncached_tokens = input_tokens - cached_tokens
        total = (
            uncached_tokens * self.input_per_million
            + cached_tokens * self.cached_input_per_million
            + output_tokens * self.output_per_million
        )
        return total / TOKENS_PER_MILLION
