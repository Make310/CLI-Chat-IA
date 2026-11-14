from dotenv import load_dotenv

from lokillo.chat import ChatService
from lokillo.cli import (
    delete_conversation,
    format_usage,
    parse_args,
    print_conversations,
    resolve_conversation,
    resolve_system_prompt,
)
from lokillo.config import create_client, load_provider_settings
from lokillo.pricing import get_pricing
from lokillo.repository import ConversationRepository

EXIT_COMMAND = "exit"


def run_chat(chat: ChatService) -> None:
    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            print("Please enter a message.")
            continue
        if user_input.lower() == EXIT_COMMAND:
            break

        print("Lokillo: ", end="", flush=True)
        for chunk in chat.send(user_input):
            print(chunk, end="", flush=True)
        print()
        print(format_usage(chat.last_message))


def main() -> None:
    load_dotenv()
    args = parse_args()
    repository = ConversationRepository()

    try:
        if args.list:
            print_conversations(repository)
            return
        if args.delete is not None:
            delete_conversation(repository, args.delete)
            return

        conversation = resolve_conversation(repository, args.resume)
        settings = load_provider_settings(args.provider, args.model)
        print(f"Using {settings.name} ({settings.model}).")
        chat = ChatService(
            client=create_client(settings),
            repository=repository,
            model=settings.model,
            instructions=resolve_system_prompt(args.system, conversation),
            temperature=args.temperature,
            conversation=conversation,
            pricing=get_pricing(settings.name, settings.model),
        )
        run_chat(chat)
    finally:
        repository.close()
