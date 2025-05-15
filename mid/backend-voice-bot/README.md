# VTuber Backend Documentation

## Overview

The VTuber Backend is a real-time communication server that processes text input, generates responses using a language model, and converts those responses to speech. It's designed to power a virtual assistant or VTuber character that can interact with users through text and voice.

## Architecture

The application follows a modular architecture with the following components:

1. **Core Server**: A FastAPI application that handles WebSocket connections and coordinates the other components.
2. **LLM Module**: Integrates with OpenRouter to generate responses using large language models.
3. **TTS Module**: Converts text to speech using edge-tts.
4. **Emotion Module**: (Currently disabled) Detects emotions and triggers interactions based on them.

## Components

### Core Server (`vtuber_backend/core/app.py`)

The main FastAPI application that:

- Handles WebSocket connections
- Manages conversation history
- Coordinates the LLM and TTS modules
- Provides a health check endpoint

### LLM Module (`vtuber_backend/llm/openRouter.py`)

Integrates with OpenRouter to generate responses using large language models:

- Supports conversation history
- Configurable model selection
- Character persona customization

### TTS Module (`vtuber_backend/tts/engine.py`)

Converts text to speech using edge-tts:

- Supports multiple languages and voices
- Caches generated audio for efficiency
- Uses the edge-tts command-line tool for reliable operation

### Emotion Module (`vtuber_backend/emotion/recognizer.py`)

(Currently disabled) Detects emotions and triggers interactions:

- Monitors for specific emotions (sad, angry)
- Generates appropriate responses based on detected emotions

## Setup and Installation

### Prerequisites

- Python 3.10+
- edge-tts command-line tool
- OpenRouter API key

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your OpenRouter API key:
   ```
   OPEN_ROUTER_API_KEY=your_api_key_here
   ```

## Usage

### Running the Server

```bash
make server
# or
python -m vtuber_backend server
```

The server will start on http://0.0.0.0:8000 and open a WebSocket endpoint at ws://localhost:8000/ws.

### Running the Client

```bash
make client
# or
python -m vtuber_backend client
```

### Testing the TTS Engine

```bash
python scripts/test_tts.py --text "Hello, this is a test." --language en
# or interactively
python scripts/test_tts.py
```

### Running the Mock TTS Server

```bash
python scripts/run_mock_tts.py
# or
python -m vtuber_backend mock-tts
```

## API Reference

### WebSocket Endpoint

**URL**: `ws://localhost:8000/ws`

#### Messages from Client to Server

**Text Input**:

```json
{
  "type": "text_input",
  "content": "Hello, how are you today?"
}
```

**Emotion Update**:

```json
{
  "type": "emotion_update",
  "emotion": "happy"
}
```

#### Messages from Server to Client

**Response**:

```json
{
  "type": "response",
  "text": "The LLM-generated response text",
  "audio": "base64_encoded_audio_data"
}
```

**Emotion Interaction** (when triggered by emotion updates):

```json
{
  "type": "emotion_interaction",
  "emotion": "sad",
  "text": "The LLM-generated response text",
  "audio": "base64_encoded_audio_data"
}
```

### HTTP Endpoints

**Health Check**:

- URL: `GET /`
- Response:
  ```json
  {
    "status": "ok",
    "message": "VTuber backend is running"
  }
  ```

## Configuration

### Environment Variables

- `OPEN_ROUTER_API_KEY`: API key for OpenRouter
- `HOST`: Host to bind the server to (default: 0.0.0.0)
- `PORT`: Port to listen on (default: 8000)
- `CHARACTER_NAME`: Name of the VTuber character (default: 點點)
- `CHARACTER_LANGUAGE`: Default language for the character (default: zh)

### LLM Configuration

The LLM module can be configured in `vtuber_backend/llm/openRouter.py`:

- `model`: Model to use (default: mistralai/mistral-7b-instruct:free)
- `max_tokens`: Maximum tokens to generate (default: 1000)
- `temperature`: Temperature for generation (default: 0.7)
- `character_name`: Name of the VTuber character (default: 點點)
- `character_persona`: Character persona description

### TTS Configuration

The TTS engine can be configured in `vtuber_backend/tts/engine.py`:

- `voice`: Default voice to use (default: zh-CN-XiaoxiaoNeural)
- `language`: Default language (default: zh)
- `use_cache`: Whether to cache generated audio (default: True)
- `cache_size`: Maximum number of items to keep in cache (default: 100)

## Supported Languages and Voices

The TTS engine supports the following languages and voices:

- Chinese: `zh-CN-XiaoxiaoNeural`
- English: `en-US-AriaNeural`
- Japanese: `ja-JP-NanamiNeural`
- Korean: `ko-KR-SunHiNeural`
- French: `fr-FR-DeniseNeural`
- German: `de-DE-KatjaNeural`
- Spanish: `es-ES-ElviraNeural`
- Italian: `it-IT-ElsaNeural`
- Russian: `ru-RU-SvetlanaNeural`
- Portuguese: `pt-BR-FranciscaNeural`

## Flow of Operation

1. Client connects to the WebSocket endpoint
2. Client sends a text input message
3. Server processes the message and adds it to the conversation history
4. Server generates a response using the LLM
5. Server converts the response to speech using edge-tts
6. Server sends the response text and audio back to the client
7. Client can update the emotion state, which is stored on the server

## Extending the Application

### Adding New Voices

To add new voices, update the `language_to_voice` dictionary in `vtuber_backend/tts/engine.py`.

### Customizing the Character Persona

To customize the character persona, update the `character_persona` parameter in the `OpenRouterLLM` constructor in `vtuber_backend/llm/openRouter.py`.

### Re-enabling Emotion Recognition

To re-enable emotion recognition, uncomment the relevant code in `vtuber_backend/core/app.py`.

## Troubleshooting

### TTS Issues

If you encounter issues with the TTS engine:

- Make sure edge-tts is installed and available in your PATH
- Check the logs for any error messages
- Try running the test script to verify that edge-tts works correctly

### LLM Issues

If you encounter issues with the LLM:

- Make sure your OpenRouter API key is valid
- Check that the model you're using is available
- Verify that you have internet connectivity

### WebSocket Connection Issues

If you have trouble connecting to the WebSocket:

- Make sure the server is running
- Check that you're using the correct URL
- Verify that there are no firewalls blocking the connection
