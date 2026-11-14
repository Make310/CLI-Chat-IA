import os

from dotenv import load_dotenv
from openai import OpenAI

from chat import ChatService
from cli import parse_args, print_conversations, resolve_conversation
from repository import ConversationRepository

INSTRUCTIONS = (
    "Tu eres un compañero que habla con jerga y acento de la costa atlantica "
    "colombiana, tienes el acento bastante marcado"
)
DEFAULT_MODEL = "gpt-6-luna"
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
    args = parse_args()
    load_dotenv()
    repository = ConversationRepository()

    try:
        if args.list:
            print_conversations(repository)
            return

        chat = ChatService(
            client=OpenAI(api_key=os.getenv("api_key")),
            repository=repository,
            model=os.getenv("model", DEFAULT_MODEL),
            instructions=INSTRUCTIONS,
            conversation=resolve_conversation(repository, args.resume),
        )
        run_chat(chat)
    finally:
        repository.close()


if __name__ == "__main__":
    main()
