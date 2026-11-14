# main.py
import os
from openai import OpenAI
from dotenv import load_dotenv
from models import Conversation, Message

load_dotenv()


INSTRUCTIONS="Tu eres un compañero que habla con jerga y acento de la costa atlantica colombiana, tienes el acento bastante marcado"
previous_response_id=None


client = OpenAI(api_key=os.getenv("api_key"))
current_conversation = Conversation()

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        if previous_response_id:
            pass
        break

    response = client.responses.create(
        model="gpt-6-luna",
        instructions=INSTRUCTIONS,
        input=user_input,
        previous_response_id=previous_response_id
    )

    output = response.output_text
    previous_response_id = response.id

    message = Message(
        user_prompt=user_input,
        system_prompt=INSTRUCTIONS,
        output_text=output
    )

    current_conversation.conversation_id = previous_response_id
    current_conversation.add_message(message=message)

    current_conversation.save()

    print(f"Lokillo: {output}")


