# Lokillo CLI

Chat de terminal con un modelo de OpenAI que responde con jerga y acento de la costa atlántica colombiana. El chat recuerda lo dicho durante la sesión y guarda cada conversación en `conversations.json`.

## Requisitos

- Python 3.12 o superior
- Una API key de OpenAI

## Instalación

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Crea un archivo `.env` en la raíz del proyecto con tu API key:

```env
api_key=sk-...
```

## Uso

```bash
python main.py
```

```
You: Hola, como estas ?
Lokillo: ¡Ajá, mi llave! Todo bien, gracias a Dios. ¿Y tú cómo vas, compae?
You: exit
```

Para salir, escribe `exit`.

## Cómo funciona

- **Memoria:** cada petición envía el `previous_response_id` de la respuesta anterior, así el modelo conserva el contexto de la sesión.
- **Guardado:** después de cada respuesta, la conversación se guarda o actualiza en `conversations.json`, bajo una clave incremental (`"1"`, `"2"`, …) por sesión.

## Estructura

```
.
├── main.py              # Bucle del chat y llamadas a la API
├── models.py            # Modelos Message y Conversation (Pydantic) y guardado en JSON
├── requirements.txt     # Dependencias del proyecto
├── conversations.json   # Historial local (se crea automáticamente, no se versiona)
└── .env                 # API key (no se versiona)
```
