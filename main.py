import os

from dotenv import load_dotenv
from openai import OpenAI

from chat import ChatService
from repository import ConversationRepository

INSTRUCTIONS = (
    "Tu eres un compañero que habla con jerga y acento de la costa atlantica colombiana, "
    "tienes el acento bastante marcado"
)


def main() -> None:
    load_dotenv()
    chat = ChatService(
        client=OpenAI(api_key=os.getenv("api_key")),
        repository=ConversationRepository(),
        model=os.getenv("model", "gpt-6-luna"),
        instructions=INSTRUCTIONS,
    )

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not user_input:
            print("Please enter a message.")
            continue
        if user_input.lower() == "exit":
            break
        print(f"Lokillo: {chat.send(user_input)}")


if __name__ == "__main__":
    main()
