#!/usr/bin/env python3
"""
Test the text-to-speech component using edge-tts.
"""

import argparse
import asyncio
import logging
import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vtuber_backend.tts.engine import TTSEngine
from vtuber_backend.utils.text import get_language_code
from vtuber_backend.utils.logging import setup_logging

logger = logging.getLogger(__name__)


async def async_main():
    """Test the text-to-speech component asynchronously."""
    # Configure logging
    setup_logging()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the TTS component")
    parser.add_argument("--text", type=str, help="Text to convert to speech")
    parser.add_argument(
        "--voice",
        type=str,
        default="zh-CN-XiaoxiaoNeural",
        help="Voice ID for edge-tts (e.g., 'zh-CN-XiaoxiaoNeural', 'en-US-AriaNeural')",
    )
    parser.add_argument("--language", type=str, help="Language code (e.g., 'zh', 'en')")
    args = parser.parse_args()

    try:
        # Create TTS engine
        tts_engine = TTSEngine(voice=args.voice)

        # Get text to convert
        if args.text:
            text = args.text

            # Detect language if not specified
            language = args.language or get_language_code(text)
            tts_engine.language = language

            print(
                f"Converting text to speech (language: {language}, voice: {tts_engine.voice})..."
            )
            await tts_engine._async_play_audio(text)
            print("Done")
        else:
            print("\nEnter text to convert to speech (Ctrl+C to exit):")
            print("Type 'exit' or 'quit' to exit")

            while True:
                try:
                    text = input("> ")
                    if text.lower() in ["exit", "quit"]:
                        break

                    # Detect language if not specified
                    language = args.language or get_language_code(text)
                    tts_engine.language = language

                    # Update voice based on language if needed
                    if (
                        args.voice == "zh-CN-XiaoxiaoNeural"
                        and language in tts_engine.language_to_voice
                    ):
                        tts_engine.voice = tts_engine.language_to_voice[language]

                    print(
                        f"Converting text to speech (language: {language}, voice: {tts_engine.voice})..."
                    )
                    await tts_engine._async_play_audio(text)
                    print("Done")

                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Error converting text to speech: {e}")

    except Exception as e:
        logger.error(f"Error in TTS test: {e}")


def main():
    """Run the async main function."""
    asyncio.run(async_main())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Error in TTS test: {e}")
