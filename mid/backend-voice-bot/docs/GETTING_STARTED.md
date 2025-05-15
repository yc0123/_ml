# Getting Started with VTuber Backend

This guide will help you get started with the VTuber backend system.

## Prerequisites

- Python 3.8 or higher
- Webcam (for emotion recognition)
- OpenRouter AI API key (for LLM)

## Installation

1. Clone the repository:

   ```bash
   cd vtuber-backend
   ```

2. Install dependencies:

   ```bash
   make install
   ```

   Or manually:

   ```bash
   pip install -r requirements.txt
   ```

3. Install the package in development mode:

   ```bash
   make dev-install
   ```

   Or manually:

   ```bash
   pip install -e .
   ```

4. Set up environment variables:

   Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

   Edit the `.env` file and add your Mistral AI API key:

   ```
   OPEN_ROUTER_API_KEY=your_api_key_here
   ```

## Running the System

### Starting the Backend Server

```bash
make server
```

Or manually:

```bash
python -m vtuber_backend server
```

This will start the FastAPI server on `http://localhost:8000` with WebSocket endpoint at `ws://localhost:8000/ws`.

### Testing with the Unity Client Simulator

```bash
make client
```

Or manually:

```bash
python -m vtuber_backend client
```

This will connect to the backend, and allow you to type messages interactively.

### Running the Mock GPT SoVITS Server

If you don't have a real GPT SoVITS server, you can use the mock server for testing:

```bash
make mock-gptsovits
```

Or manually:

```bash
python -m vtuber_backend mock-gptsovits
```

## Testing Individual Components

### Testing Emotion Recognition

```bash
make test-emotion
```

Or manually:

```bash
python scripts/test_emotion_recognition.py
```

This will open a window showing your webcam feed with detected emotions overlaid.

### Testing Text-to-Speech

```bash
make test-tts
```

Or manually:

```bash
python scripts/test_tts.py --use-mock
```

This will start a mock GPT SoVITS server and allow you to enter text to be converted to speech.

### Testing LLM

```bash
make test-llm
```   

Or manually:

```bash
python scripts/test_llm.py
```

This will allow you to interact with the Mistral AI LLM.

## Integrating with Unity

To integrate with Unity, you need to:

1. Connect to the WebSocket endpoint at `ws://localhost:8000/ws`
2. Send messages in the format described in the README.md
3. Handle responses from the backend

See the `src/vtuber_backend/core/unity_client.py` file for an example of how to connect to the backend.

## Troubleshooting

### Emotion Recognition Issues

- Make sure your webcam is connected and working
- Check that you have installed the required dependencies for DeepFace
- Try adjusting the detection frequency with the `--frequency` parameter

### TTS Issues

- If using the mock server, make sure it's running
- If using a real GPT SoVITS server, check that the URL is correct
- Verify that the language code is supported

### LLM Issues

- Check that your Mistral AI API key is correct
- Verify that you have internet connectivity
- Try adjusting the model parameters like temperature

## Next Steps

- Customize the character persona in `vtuber_backend/llm/openRouter.py`
- Adjust emotion triggers in `vtuber_backend/core/app.py`
- Implement the WebSocket client in your Unity frontend
