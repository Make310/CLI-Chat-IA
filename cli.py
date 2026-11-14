import argparse

from models import Conversation
from repository import ConversationRepository

PREVIEW_LENGTH = 50


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lokillo CLI chat")
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
