from decimal import Decimal

from lokillo.models import ModelPricing

FREE = ModelPricing(
    input_per_million=Decimal("0"),
    cached_input_per_million=Decimal("0"),
    output_per_million=Decimal("0"),
)

# Standard API rates. Check https://developers.openai.com/api/docs/pricing
OPENAI_PRICING = {
    "gpt-6-luna": ModelPricing(
        input_per_million=Decimal("0.10"),
        cached_input_per_million=Decimal("0.01"),
        output_per_million=Decimal("0.50"),
    ),
}


def get_pricing(provider: str, model: str) -> ModelPricing | None:
    """Returns the model's pricing, or None if it is unknown.

    Local models served by Ollama are free.
    """
    if provider == "ollama":
        return FREE
    return OPENAI_PRICING.get(model)
