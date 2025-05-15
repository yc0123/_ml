#!/usr/bin/env python3
"""
Unity client for the VTuber backend.

This module provides a client for Unity to connect to the VTuber backend.
It can also be used as a standalone client for testing.
"""
import asyncio
import base64
import json
import logging
import os
import tempfile
from typing import Optional, Dict, Any, Callable

import websockets
from pygame import mixer

from vtuber_backend.utils.logging import setup_logging

logger = logging.getLogger(__name__)


class UnityClient:
    """Client for Unity to connect to the VTuber backend."""

    def __init__(self, websocket_url: str = "ws://localhost:8000/ws"):
        """
        Initialize the Unity client.
        
        Args:
            websocket_url: WebSocket URL of the backend
        """
        self.websocket_url = websocket_url
        self.websocket = None
        self.running = False
        
        # Initialize audio playback
        mixer.init()
        
        # Callbacks
        self.on_response: Optional[Callable[[str, str], None]] = None
        self.on_emotion_interaction: Optional[Callable[[str, str, str], None]] = None
        self.on_connect: Optional[Callable[[], None]] = None
        self.on_disconnect: Optional[Callable[[], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

    async def connect(self) -> bool:
        """
        Connect to the backend WebSocket.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            logger.info(f"Connected to {self.websocket_url}")
            self.running = True
            
            if self.on_connect:
                self.on_connect()
                
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            
            if self.on_error:
                self.on_error(f"Connection failed: {e}")
                
            return False

    async def disconnect(self):
        """Disconnect from the backend WebSocket."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.running = False
            logger.info("Disconnected from backend")
            
            if self.on_disconnect:
                self.on_disconnect()

    async def send_text_input(self, text: str):
        """
        Send text input to the backend.
        
        Args:
            text: Text input from the user
        """
        if not self.websocket:
            logger.error("Not connected to backend")
            return
            
        try:
            message = {
                "type": "text_input",
                "content": text
            }
            await self.websocket.send(json.dumps(message))
            logger.info(f"Sent text input: {text}")
        except Exception as e:
            logger.error(f"Failed to send text input: {e}")
            
            if self.on_error:
                self.on_error(f"Failed to send text: {e}")

    async def send_emotion_update(self, emotion: str):
        """
        Send emotion update to the backend.
        
        Args:
            emotion: Detected emotion (e.g., "happy", "sad", "angry")
        """
        if not self.websocket:
            logger.error("Not connected to backend")
            return
            
        try:
            message = {
                "type": "emotion_update",
                "emotion": emotion
            }
            await self.websocket.send(json.dumps(message))
            logger.info(f"Sent emotion update: {emotion}")
        except Exception as e:
            logger.error(f"Failed to send emotion update: {e}")
            
            if self.on_error:
                self.on_error(f"Failed to send emotion: {e}")

    async def receive_messages(self):
        """
        Receive and process messages from the backend.
        
        This method runs in a loop until disconnected.
        """
        if not self.websocket:
            logger.error("Not connected to backend")
            return
            
        while self.running:
            try:
                message = await self.websocket.recv()
                data = json.loads(message)
                
                # Process different message types
                if data["type"] == "response":
                    await self._handle_response(data)
                elif data["type"] == "emotion_interaction":
                    await self._handle_emotion_interaction(data)
                else:
                    logger.warning(f"Unknown message type: {data['type']}")
                    
            except websockets.exceptions.ConnectionClosed:
                logger.info("Connection closed")
                self.running = False
                
                if self.on_disconnect:
                    self.on_disconnect()
                    
                break
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                
                if self.on_error:
                    self.on_error(f"Error receiving message: {e}")
                    
                await asyncio.sleep(1)  # Prevent tight loop on error

    async def _handle_response(self, data: Dict[str, Any]):
        """
        Handle a response message from the backend.
        
        Args:
            data: Response data
        """
        text = data.get("text", "")
        audio = data.get("audio")
        
        logger.info(f"Received response: {text}")
        
        # Play audio if available
        if audio:
            await self._play_audio(audio)
            
        # Call callback if set
        if self.on_response:
            self.on_response(text, audio)

    async def _handle_emotion_interaction(self, data: Dict[str, Any]):
        """
        Handle an emotion interaction message from the backend.
        
        Args:
            data: Emotion interaction data
        """
        emotion = data.get("emotion", "")
        text = data.get("text", "")
        audio = data.get("audio")
        
        logger.info(f"Received emotion interaction: {emotion}")
        logger.info(f"Response: {text}")
        
        # Play audio if available
        if audio:
            await self._play_audio(audio)
            
        # Call callback if set
        if self.on_emotion_interaction:
            self.on_emotion_interaction(emotion, text, audio)

    async def _play_audio(self, audio_base64: str):
        """
        Play audio from base64-encoded data.
        
        Args:
            audio_base64: Base64-encoded audio data
        """
        try:
            # Decode base64
            audio_data = base64.b64decode(audio_base64)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Play audio
            mixer.music.load(temp_file_path)
            mixer.music.play()
            
            # Wait for playback to finish
            while mixer.music.get_busy():
                await asyncio.sleep(0.1)
            
            # Clean up
            os.unlink(temp_file_path)
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            
            if self.on_error:
                self.on_error(f"Error playing audio: {e}")


class UnityClientSimulator:
    """
    Simulates a Unity client for testing.
    
    This class provides a simple command-line interface for testing
    the VTuber backend without Unity.
    """
    
    def __init__(self, websocket_url: str = "ws://localhost:8000/ws"):
        """
        Initialize the Unity client simulator.
        
        Args:
            websocket_url: WebSocket URL of the backend
        """
        self.client = UnityClient(websocket_url)
        self.receive_task = None
        
        # Set up callbacks
        self.client.on_response = self._on_response
        self.client.on_emotion_interaction = self._on_emotion_interaction
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_error = self._on_error
        
    def _on_response(self, text: str, audio: str):
        """Handle response from backend."""
        print(f"\nResponse: {text}")
        print("> ", end="", flush=True)
        
    def _on_emotion_interaction(self, emotion: str, text: str, audio: str):
        """Handle emotion interaction from backend."""
        print(f"\nEmotion interaction ({emotion}): {text}")
        print("> ", end="", flush=True)
        
    def _on_connect(self):
        """Handle connection to backend."""
        print("Connected to backend")
        
    def _on_disconnect(self):
        """Handle disconnection from backend."""
        print("\nDisconnected from backend")
        
    def _on_error(self, error: str):
        """Handle error from backend."""
        print(f"\nError: {error}")
        print("> ", end="", flush=True)
        
    async def run(self):
        """Run the Unity client simulator."""
        # Connect to backend
        if not await self.client.connect():
            return
        
        try:
            # Start receiving messages in the background
            self.receive_task = asyncio.create_task(self.client.receive_messages())
            
            # Simulate user interaction
            await asyncio.sleep(1)
            
            # Wait for user input
            print("\nType messages to send to the backend (Ctrl+C to exit):")
            print("Type 'emotion: [emotion]' to send an emotion update")
            print("> ", end="", flush=True)
            
            while True:

                try:
                    user_input = await asyncio.get_event_loop().run_in_executor(None, input, "")
                    
                    if user_input.lower() in ["exit", "quit"]:
                        break
                        
                    # Check for emotion update
                    if user_input.lower().startswith("emotion:"):
                        emotion = user_input.split(":", 1)[1].strip()
                        await self.client.send_emotion_update(emotion)
                    else:
                        await self.client.send_text_input(user_input)
                        
                    print("> ", end="", flush=True)
                except KeyboardInterrupt:
                    break
        
        finally:
            # Clean up
            if self.receive_task:
                self.receive_task.cancel()
                try:
                    await self.receive_task
                except asyncio.CancelledError:
                    pass
            
            await self.client.disconnect()


async def main():
    """Main function for the Unity client simulator."""
    # Configure logging
    setup_logging()
    
    # Create and run simulator
    simulator = UnityClientSimulator()
    await simulator.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
