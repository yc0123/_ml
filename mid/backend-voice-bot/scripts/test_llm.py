#!/usr/bin/env python3
"""
Test the LLM component.
"""

import argparse
import logging
import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from vtuber_backend.llm.openRouter import OpenRouterLLM
from vtuber_backend.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Test the LLM component."""
    # Configure logging
    setup_logging()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the LLM component")
    parser.add_argument("--api-key", type=str, help="OpenRouter API key")
    parser.add_argument(
        "--model",
        type=str,
        default="mistralai/mistral-7b-instruct:free",
        help="Model to use",
    )
    parser.add_argument(
        "--temperature", type=float, default=0.7, help="Temperature for generation"
    )
    parser.add_argument(
        "--character-name", type=str, default="mochi", help="Character name"
    )
    parser.add_argument("--prompt", type=str, help="Single prompt to test")
    args = parser.parse_args()

    # Get API key from arguments or environment
    api_key = "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"

    try:
        # Create LLM client
        llm = OpenRouterLLM(
            api_key=api_key,
            model=args.model,
            temperature=args.temperature,
            character_name=args.character_name,
        )

        # Test with a single prompt if provided
        if args.prompt:
            print(f"\nPrompt: {args.prompt}")
            response = llm.generate_response(args.prompt)
            print(f"Response: {response}")
            return

        # Interactive mode
        print("\nEnter prompts to test the LLM (Ctrl+C to exit):")
        print("Type 'exit' or 'quit' to exit")
        print("Type 'emotion: [emotion]' to test emotion responses")

        conversation = []

        while True:
            try:
                prompt = input("> ")
                if prompt.lower() in ["exit", "quit"]:
                    break

                # Check for emotion test
                if prompt.lower().startswith("emotion:"):
                    emotion = prompt.split(":", 1)[1].strip()
                    print(f"Testing emotion response for: {emotion}")
                    response = llm.generate_emotion_response(emotion)
                else:
                    # Add to conversation history
                    conversation.append({"role": "user", "content": prompt})

                    # Generate response
                    response = llm.generate_response(prompt, conversation)

                    # Add to conversation history
                    conversation.append({"role": "assistant", "content": response})

                    # Limit conversation history
                    if len(conversation) > 20:
                        conversation = conversation[-20:]

                print(f"Response: {response}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error generating response: {e}")

    except Exception as e:
        logger.error(f"Error initializing LLM: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Error in LLM test: {e}")
