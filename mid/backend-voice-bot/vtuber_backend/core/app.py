"""
Main FastAPI application for the VTuber backend.
"""
import json
import logging
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from vtuber_backend.emotion.recognizer import EmotionRecognizer
from vtuber_backend.llm.openRouter import OpenRouterLLM
from vtuber_backend.tts.engine import TTSEngine
from vtuber_backend.utils.logging import setup_logging

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from openai import OpenAI
import os


class CustomE5Embedding(HuggingFaceEmbeddings):
    def embed_documents(self, texts):
        texts = [f"passage: {t}" for t in texts]
        return super().embed_documents(texts)

    def embed_query(self, text):
        return super().embed_query(f"query: {text}")
    
embedding_model = CustomE5Embedding(model_name="intfloat/multilingual-e5-small")
db = FAISS.load_local("faiss_db", embedding_model, allow_dangerous_deserialization=True)
retriever = db.as_retriever()

prompt_template = """根據下列資料回答問題：{retrieved_chunks}
使用者的問題是：{question}
請根據資料內容回覆，若資料不足請告訴同學可以請教金門大學的老師。"""

# Setup logging
logger = logging.getLogger(__name__)
setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="VTuber Backend", description="Backend for VTuber personal assistant"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize components
llm = OpenRouterLLM()
tts_engine = TTSEngine()
emotion_recognizer = None  # Will be initialized when needed

# Store active connections
active_connections: List[WebSocket] = []

# Store conversation history for each connection
conversation_history: Dict[str, List[Dict]] = {}

# Store emotion state
emotion_state: Dict[str, str] = {}


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    # Emotion recognition is disabled for now
    # global emotion_recognizer
    # try:
    #     emotion_recognizer = EmotionRecognizer()
    #     # Start emotion monitoring in background
    #     asyncio.create_task(monitor_emotions())
    # except Exception as e:
    #     logger.error(f"Failed to initialize emotion recognizer: {e}")
    #     # Continue without emotion recognition if it fails
    pass


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    # if emotion_recognizer:
    #     emotion_recognizer.stop()
    pass


# async def monitor_emotions():
#     """Background task to monitor emotions and trigger interactions."""
#     if not emotion_recognizer:
#         logger.warning("Emotion recognizer not available, skipping monitoring")
#         return
#
#     while True:
#         try:
#             emotion = emotion_recognizer.get_current_emotion()
#             if emotion in ["sad", "angry"] and active_connections:
#                 # Trigger interaction for sad or angry emotions
#                 for connection in active_connections:
#                     conn_id = str(id(connection))
#                     if emotion_state.get(conn_id) != emotion:
#                         emotion_state[conn_id] = emotion
#                         await trigger_emotion_interaction(connection, emotion)
#             await asyncio.sleep(5)  # Check every 5 seconds
#         except Exception as e:
#             logger.error(f"Error in emotion monitoring: {e}")
#             await asyncio.sleep(10)  # Wait longer on error


async def trigger_emotion_interaction(websocket: WebSocket, emotion: str):
    """Trigger an interaction based on detected emotion."""
    try:
        # Generate appropriate response based on emotion
        if emotion == "sad":
            prompt = "The user looks sad. Ask if they're okay in a caring way."
        elif emotion == "angry":
            prompt = "The user looks upset. Ask if something is bothering them."
        else:
            return

        # Generate response with LLM
        response = llm.generate_response(prompt, [])

        # Generate speech
        audio_data = tts_engine.generate_speech(response)

        # Send to client
        await websocket.send_json(
            {
                "type": "emotion_interaction",
                "emotion": emotion,
                "text": response,
                "audio": audio_data,  # Base64 encoded audio
            }
        )
    except Exception as e:
        logger.error(f"Error triggering emotion interaction: {e}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await websocket.accept()
    active_connections.append(websocket)
    conn_id = str(id(websocket))

    # Initialize conversation history for this connection
    if conn_id not in conversation_history:
        conversation_history[conn_id] = []

    try:
        while True:
            logger.info("Waiting for message from client...")
            data = await websocket.receive_text()
            logger.info(f"Received message from client: {data}")
            request = json.loads(data)

            if request["type"] == "text_input":
                logger.info(f"Processing text input: {request['content']}")
                # Process text input with LLM
                user_input = request["content"]
                history = conversation_history[conn_id]

                # Add user message to history
                # history.append({"role": "user", "content": user_input})

                # Generate response with LLM
                logger.info("Generating response with LLM...")
                docs = retriever.get_relevant_documents(user_input)
                retrieved_chunks = "\n\n".join([doc.page_content for doc in docs])
                final_prompt = prompt_template.format(retrieved_chunks=retrieved_chunks, question=user_input)
                history.append({"role": "user", "content": final_prompt})
                response_text = llm.generate_response(prompt=final_prompt, conversation_history=history)
                logger.info(f"Generated response: {response_text}")

                # Add assistant response to history
                history.append({"role": "assistant", "content": response_text})

                # Limit history size
                if len(history) > 20:
                    history = history[-20:]
                conversation_history[conn_id] = history

                # Generate speech
                logger.info("Generating speech...")
                audio_data = tts_engine.generate_speech(response_text)
                logger.info("Speech generated successfully")

                # Send response
                logger.info("Sending response to client...")
                await websocket.send_json(
                    {
                        "type": "response",
                        "text": response_text,
                        "audio": audio_data,  # Base64 encoded
                    }
                )
                logger.info("Response sent to client")

            elif request["type"] == "emotion_update":
                # Handle emotion updates from Unity (if any)
                if "emotion" in request:
                    emotion_state[conn_id] = request["emotion"]

    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {conn_id}")
        active_connections.remove(websocket)
        # Keep conversation history for potential reconnection

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"status": "ok", "message": "VTuber backend is running"}


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server."""
    uvicorn.run("vtuber_backend.core.app:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    run_server()
