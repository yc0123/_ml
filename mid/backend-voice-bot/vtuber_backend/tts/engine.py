#!/usr/bin/env python3
"""
Text-to-speech module using edge-tts.
"""

import base64
import logging
import os
import subprocess
import tempfile
import unicodedata
from typing import Dict, Optional

from mutagen.mp3 import MP3
from pygame import mixer

logger = logging.getLogger(__name__)


class TTSEngine:
    """Text-to-speech engine using edge-tts."""

    def __init__(
        self,
        voice: str = "zh-CN-XiaoxiaoNeural",
        language: str = "zh",
        use_cache: bool = True,
        cache_size: int = 100,
    ):
        """
        Initialize the TTS engine.

        Args:
            voice: Voice ID for edge-tts (default: 'zh-CN-XiaoxiaoNeural' for Mandarin)
            language: Language code (default: 'zh' for Mandarin)
            use_cache: Whether to cache generated audio
            cache_size: Maximum number of items to keep in cache
        """
        self.voice = voice
        self.language = language
        self.use_cache = use_cache
        self.cache_size = cache_size
        self.cache: Dict[str, str] = {}  # text -> base64 audio

        # Initialize mixer for playback
        mixer.init()

        # Map language codes to edge-tts voice IDs
        self.language_to_voice = {
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

    def _generate_with_edge_tts_cli(self, text: str, output_file: str) -> bool:
        """
        Generate speech using edge-tts command-line tool.

        Args:
            text: Text to convert to speech
            output_file: Path to save the audio file

        Returns:
            True if successful, False otherwise
        """
        # Select voice based on language if not explicitly set
        voice = self.voice
        if (
            self.language in self.language_to_voice
            and self.voice == "zh-CN-XiaoxiaoNeural"
        ):
            voice = self.language_to_voice[self.language]

        try:
            # Create a temporary file for the text
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".txt", encoding="utf-8"
            ) as text_file:
                text_file.write(text)
                text_file_path = text_file.name

            # Run edge-tts command
            cmd = [
                "edge-tts",
                "--voice",
                voice,
                "--file",
                text_file_path,
                "--write-media",
                output_file,
            ]

            logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,  # 10 seconds timeout
            )

            # Clean up text file
            os.unlink(text_file_path)

            if result.returncode != 0:
                logger.error(f"edge-tts command failed: {result.stderr}")
                return False

            logger.debug(f"Audio saved as {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error generating speech with edge-tts CLI: {e}")
            return False

    def generate_speech(self, text: str) -> str:
        """
        Generate speech from text.

        Args:
            text: Text to convert to speech

        Returns:
            Base64-encoded audio data
        """
        # Check cache first
        if self.use_cache and text in self.cache:
            return self.cache[text]

        try:
            logger.info(f"Starting speech generation for text: {text[:30]}...")

            # Attempt to encode text, ignoring any unencodable characters
            text = self.sanitize_text(text)

            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file_path = temp_file.name

            # Generate speech with edge-tts CLI
            success = self._generate_with_edge_tts_cli(text, temp_file_path)

            if not success:
                logger.error("Failed to generate speech")
                return ""

            # Read the file and encode to base64
            with open(temp_file_path, "rb") as f:
                audio_data = base64.b64encode(f.read()).decode("utf-8")

            # Clean up
            os.unlink(temp_file_path)

            # Cache the result
            if self.use_cache:
                self._update_cache(text, audio_data)

            return audio_data

        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            # Return empty string instead of raising exception
            return ""
        
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Remove characters that are likely unsupported by edge-tts (e.g., emoji, control characters).
        """
        def is_valid_char(c):
            try:
                # Remove control characters and emoji
                return (
                    unicodedata.category(c)[0] != "C" and  # control character
                    not (0x1F000 <= ord(c) <= 0x1FAFF)  # emoji range
                )
            except Exception:
                return False

        return ''.join(c for c in text if is_valid_char(c))

    def _update_cache(self, text: str, audio_data: str):
        """
        Update the cache with new audio data.

        Args:
            text: The text key
            audio_data: Base64-encoded audio data
        """
        # Add to cache
        self.cache[text] = audio_data

        # Trim cache if it exceeds the maximum size
        if len(self.cache) > self.cache_size:
            # Remove oldest items (assuming insertion order is maintained in Python 3.7+)
            items_to_remove = len(self.cache) - self.cache_size
            for key in list(self.cache.keys())[:items_to_remove]:
                del self.cache[key]

    def play_audio(self, text: str) -> None:
        """
        Generate and play audio for the given text.

        Args:
            text: Text to convert to speech and play
        """
        try:
            # Generate audio
            audio_data = self.generate_speech(text)

            if not audio_data:
                logger.error("No audio data generated")
                return

            # Decode base64
            audio_bytes = base64.b64decode(audio_data)

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name

            # Play audio
            mixer.music.load(temp_file_path)
            mixer.music.play()

            # Wait for playback to finish
            audio_length = MP3(temp_file_path).info.length
            import time

            time.sleep(audio_length + 0.5)  # Add a small buffer

            # Clean up
            os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"Error playing audio: {e}")
