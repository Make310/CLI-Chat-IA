# Lokillo CLI

Terminal chat with an OpenAI model that replies using the slang and accent of Colombia's Caribbean coast. The chat remembers what was said during the session and stores every conversation in a local SQLite database.

## Requirements

- Python 3.12 or higher
- An OpenAI API key

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
api_key=sk-...
model=gpt-6-luna   # optional, this is the default value
```

## Usage

```bash
python main.py
```

```
You: Hola, como estas ?
Lokillo: ¡Ajá, mi llave! Todo bien, gracias a Dios. ¿Y tú cómo vas, compae?
You: exit
```

Type `exit` (or press Ctrl+C / Ctrl+D) to quit.

## How it works

- **Memory:** each request sends the `previous_response_id` of the previous response, so the model keeps the session context.
- **Storage:** after each response, the conversation is saved to a SQLite database (`conversations.db`) with two tables: `conversations` and `messages`. The database and tables are created automatically.

To query the history:

```bash
sqlite3 conversations.db "SELECT user_prompt, output_text FROM messages WHERE conversation_id = 1;"
```

## Project structure

```
.
├── main.py              # Entry point: configuration and terminal loop
├── chat.py              # ChatService: API calls and session memory
├── models.py            # Message and Conversation models (Pydantic)
├── repository.py        # SQLite persistence
├── requirements.txt     # Project dependencies
├── conversations.db     # Local history (created automatically, not versioned)
└── .env                 # API key (not versioned)
```
