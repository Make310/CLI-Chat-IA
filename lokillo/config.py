import os

from openai import OpenAI
from pydantic import BaseModel

PROVIDERS = ("openai", "ollama")
DEFAULT_PROVIDER = "openai"


class ProviderSettings(BaseModel):
    name: str
    api_key: str | None
    base_url: str | None
    model: str


def load_provider_settings(provider: str) -> ProviderSettings:
    """Reads the provider's settings from the environment."""
    if provider == "ollama":
        return ProviderSettings(
            name=provider,
            api_key="ollama",  # not validated by Ollama, required by the SDK
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            model=os.getenv("OLLAMA_MODEL", "gemma3:12b"),
        )
    return ProviderSettings(
        name=provider,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=None,  # official OpenAI endpoint
        model=os.getenv("OPENAI_MODEL", "gpt-6-luna"),
    )


def create_client(settings: ProviderSettings) -> OpenAI:
    return OpenAI(api_key=settings.api_key, base_url=settings.base_url)
