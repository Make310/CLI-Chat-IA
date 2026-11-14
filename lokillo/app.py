from dotenv import load_dotenv

from lokillo.chat import ChatService
from lokillo.cli import parse_args, print_conversations, resolve_conversation
from lokillo.config import create_client, load_provider_settings
from lokillo.repository import ConversationRepository

INSTRUCTIONS = (
    "Tu eres un compañero que habla con jerga y acento de la costa atlantica "
    "colombiana, tienes el acento bastante marcado"
)
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

        print(f"Lokillo: {chat.send(user_input)}")


def main() -> None:
    load_dotenv()
    args = parse_args()
    repository = ConversationRepository()

    try:
        if args.list:
            print_conversations(repository)
            return

        conversation = resolve_conversation(repository, args.resume)
        settings = load_provider_settings(args.provider)
        print(f"Using {settings.name} ({settings.model}).")
        chat = ChatService(
            client=create_client(settings),
            repository=repository,
            model=settings.model,
            instructions=INSTRUCTIONS,
            conversation=conversation,
        )
        run_chat(chat)
    finally:
        repository.close()
