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

Copy the example environment file and add your OpenAI API key:

```bash
cp .env.example .env
```

```env
# Active provider: openai | ollama (can be overridden with --provider)
PROVIDER=openai

# OpenAI (cloud)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-6-luna

# Ollama (local)
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=gemma3:12b
```

To use a local model, install [Ollama](https://ollama.com) and pull the model (`ollama pull gemma3:12b`).

## Usage

```bash
python main.py                     # uses PROVIDER from .env
python main.py --provider ollama   # local model
python main.py --provider openai   # cloud model
```

```
Using openai (gpt-6-luna).
You: Hola, como estas ?
Lokillo: ¡Ajá, mi llave! Todo bien, gracias a Dios. ¿Y tú cómo vas, compae?
You: exit
```

Type `exit` (or press Ctrl+C / Ctrl+D) to quit. Replies are streamed token by token.

### Options

| Flag | Description |
|---|---|
| `--provider {openai,ollama}` | LLM provider (default: `PROVIDER` from `.env`) |
| `--model NAME` | Model to use (default: the provider's model from `.env`) |
| `--temperature N` | Sampling temperature between 0 and 2 (default: model default) |
| `--system "PROMPT"` | System prompt (default: the resumed conversation's prompt, or Lokillo) |

```bash
python main.py --system "Eres un tutor de Python" --temperature 0.2
python main.py --provider ollama --model llama3.2
```

### Managing conversations

```bash
python main.py --list        # show recent conversations
python main.py --resume 1    # continue conversation 1
python main.py --delete 1    # delete conversation 1 and its messages
```

```
[2] 2026-11-14 03:42:30  (1 messages)  Buenas, que más
[1] 2026-11-14 03:40:12  (3 messages)  Me llamo Pedro
```

## How it works

- **Memory:** the full user/assistant history is loaded from the database and sent with every request, so the model keeps the context. This works with any OpenAI-compatible provider, including local models served by Ollama.
- **Usage and cost:** after each reply, the input/output tokens and the estimated cost in USD are shown, e.g. `[tokens: 153 in / 25 out · cost: $0.000028]`. Prices live in `lokillo/pricing.py`; local Ollama models cost $0, and models without a price show `unknown`.
- **Storage:** after each response, the conversation is saved to a SQLite database (`data/conversations.db`) with two tables: `conversations` and `messages`. The database and tables are created automatically.

To query the history:

```bash
sqlite3 data/conversations.db "SELECT user_prompt, output_text FROM messages WHERE conversation_id = 1;"
```

## Project structure

```
.
├── main.py                  # Entry point
├── lokillo/                 # Application package
│   ├── app.py               # Wiring and terminal loop
│   ├── cli.py               # Command-line arguments and conversation listing
│   ├── config.py            # Provider settings (OpenAI / Ollama) and client factory
│   ├── chat.py              # ChatService: API calls and session memory
│   ├── models.py            # Message and Conversation models (Pydantic)
│   ├── pricing.py           # Model prices and cost calculation
│   └── repository.py        # SQLite persistence
├── data/
│   └── conversations.db     # Local history (created automatically, not versioned)
├── requirements.txt         # Project dependencies
├── .env.example             # Environment variables template
└── .env                     # API keys and settings (not versioned)
```
