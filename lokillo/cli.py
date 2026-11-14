import argparse
import os

from lokillo.config import DEFAULT_PROVIDER, DEFAULT_SYSTEM_PROMPT, PROVIDERS
from lokillo.models import Conversation
from lokillo.repository import ConversationRepository

PREVIEW_LENGTH = 50
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 2.0


def temperature(value: str) -> float:
    """Argparse type that accepts a float between 0 and 2."""
    number = float(value)
    if not MIN_TEMPERATURE <= number <= MAX_TEMPERATURE:
        raise argparse.ArgumentTypeError(
            f"must be between {MIN_TEMPERATURE} and {MAX_TEMPERATURE}"
        )
    return number


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lokillo CLI chat")
    parser.add_argument(
        "--provider",
        choices=PROVIDERS,
        default=os.getenv("PROVIDER", DEFAULT_PROVIDER),
        help="LLM provider to use (default: PROVIDER from .env)",
    )
    parser.add_argument(
        "--model",
        help="model to use (default: the provider's model from .env)",
    )
    parser.add_argument(
        "--temperature",
        type=temperature,
        help="sampling temperature between 0 and 2 (default: model default)",
    )
    parser.add_argument(
        "--system",
        metavar="PROMPT",
        help="system prompt (default: the resumed conversation's or Lokillo)",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--list",
        action="store_true",
        help="list recent conversations",
    )
    group.add_argument(
        "--resume",
        type=int,
        metavar="ID",
        help="resume the conversation with this ID",
    )
    group.add_argument(
        "--delete",
        type=int,
        metavar="ID",
        help="delete the conversation with this ID",
    )
    return parser.parse_args()


def truncate(text: str, max_length: int = PREVIEW_LENGTH) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def print_conversations(repository: ConversationRepository) -> None:
    summaries = repository.list_conversations()
    if not summaries:
        print("No conversations yet.")
        return

    for summary in summaries:
        print(
            f"[{summary.id}] {summary.updated_at}  "
            f"({summary.message_count} messages)  "
            f"{truncate(summary.first_prompt)}"
        )


def delete_conversation(
    repository: ConversationRepository,
    conversation_id: int,
) -> None:
    if not repository.delete_conversation(conversation_id):
        raise SystemExit(f"Conversation {conversation_id} not found.")
    print(f"Conversation {conversation_id} deleted.")


def resolve_conversation(
    repository: ConversationRepository,
    resume_id: int | None,
) -> Conversation | None:
    """Returns the conversation to resume, or None to start a new one."""
    if resume_id is None:
        return None

    conversation = repository.get_conversation(resume_id)
    if conversation is None:
        raise SystemExit(
            f"Conversation {resume_id} not found. "
            "Use --list to see available conversations."
        )

    print(f"Resuming conversation {conversation.id}.")
    return conversation


def resolve_system_prompt(
    system: str | None,
    conversation: Conversation | None,
) -> str:
    """Picks the --system flag, then the resumed prompt, then the default."""
    if system:
        return system
    if conversation and conversation.messages:
        return conversation.messages[-1].system_prompt
    return DEFAULT_SYSTEM_PROMPT
