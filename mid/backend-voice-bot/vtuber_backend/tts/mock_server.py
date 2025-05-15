#!/usr/bin/env python3
"""
Mock TTS server for development and testing using edge-tts.
"""

import asyncio
import base64
import json
import logging
import os
import signal
import tempfile
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import edge_tts

logger = logging.getLogger(__name__)


class MockTTSServer:
    """
    A simple HTTP server that provides a TTS API for development.

    This is useful for testing the integration without having to modify the client code.
    """

    def __init__(self, host: str = "localhost", port: int = 8080):
        """
        Initialize the mock server.

        Args:
            host: Host to bind to
            port: Port to listen on
        """
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.url = f"http://{host}:{port}"

    def start(self):
        """Start the mock server."""
        if self.server:
            logger.warning("Server already running")
            return

        # Create handler class with access to server instance
        server_instance = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                # Redirect logs to our logger
                logger.debug(format % args)

            def do_GET(self):
                if self.path == "/health":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "ok"}).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            async def generate_speech(self, text, voice):
                """Generate speech using edge-tts."""
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".mp3"
                ) as temp_file:
                    temp_file_path = temp_file.name

                # Create communicate object
                tts = edge_tts.Communicate(text, voice)

                # Save audio to file
                await tts.save(temp_file_path)

                # Read the file and encode to base64
                with open(temp_file_path, "rb") as f:
                    audio_data = base64.b64encode(f.read()).decode("utf-8")

                # Clean up
                os.unlink(temp_file_path)

                return audio_data

            def do_POST(self):
                if self.path == "/tts":
                    content_length = int(self.headers["Content-Length"])
                    post_data = self.rfile.read(content_length).decode("utf-8")
                    request = json.loads(post_data)

                    # Get parameters
                    text = request.get("text", "")
                    language = request.get("language", "zh")
                    speaker_id = request.get("speaker_id", "default")

                    # Map language codes to edge-tts voice IDs
                    language_to_voice = {
                        "zh": "zh-CN-XiaoxiaoNeural",
                        "en": "en-US-AriaNeural",
                        "ja": "ja-JP-NanamiNeural",
                        "ko": "ko-KR-SunHiNeural",
                        "fr": "fr-FR-DeniseNeural",
                        "de": "de-DE-KatjaNeural",
                        "es": "es-ES-ElviraNeural",
                        "it": "it-IT-ElsaNeural",
                        "ru": "ru-RU-SvetlanaNeural",
                        "pt": "pt-BR-FranciscaNeural",
                    }

                    # Select voice based on language
                    voice = language_to_voice.get(language, "zh-CN-XiaoxiaoNeural")

                    # Generate audio with edge-tts
                    # We need to handle this differently since we can't use asyncio.run() in a thread
                    # that already has an event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    audio_data = loop.run_until_complete(
                        self.generate_speech(text, voice)
                    )
                    loop.close()

                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"audio": audio_data}).encode())
                else:
                    self.send_response(404)
                    self.end_headers()

        # Create and start server
        self.server = HTTPServer((self.host, self.port), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        logger.info(f"Mock TTS server started at {self.url}")

    def stop(self):
        """Stop the mock server."""
        if not self.server:
            logger.warning("Server not running")
            return

        self.server.shutdown()
        self.server.server_close()
        if self.thread:
            self.thread.join(timeout=5.0)
        self.server = None
        self.thread = None
        logger.info("Mock TTS server stopped")


async def run_server(host: str = "localhost", port: int = 8080):
    """
    Run the mock TTS server as a standalone application.

    Args:
        host: Host to bind to
        port: Port to listen on
    """
    # Create and start server
    server = MockTTSServer(host=host, port=port)
    server.start()

    logger.info(f"Mock TTS server running at http://{host}:{port}")
    logger.info("Press Ctrl+C to stop")

    # Set up signal handling for graceful shutdown
    loop = asyncio.get_running_loop()

    def signal_handler():
        logger.info("Shutting down...")
        server.stop()
        loop.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    # Keep the server running
    while True:
        await asyncio.sleep(3600)  # Sleep for an hour


if __name__ == "__main__":
    import signal

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nExiting...")
