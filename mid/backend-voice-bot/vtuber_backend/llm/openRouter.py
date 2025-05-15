"""
OpenRouter integration for the VTuber backend.
"""

import logging
import os
import json
import requests
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class OpenRouterLLM:
    """OpenRouter client for the VTuber backend."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "deepseek/deepseek-chat-v3-0324:free",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        character_name: str = "Nana",
        character_persona: Optional[str] = None,
    ):
        """
        Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key (defaults to environment variable)
            model: Model to use (default is Claude 3 Opus)
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            character_name: Name of the VTuber character
            character_persona: Character persona description
        """
        # Use provided API key or get from environment
        self.api_key = "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"

        if not self.api_key:
            logger.error("No OpenRouter API key provided")
            raise ValueError("OpenRouter API key is required")

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.character_name = character_name
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        # Set default persona if not provided
        if character_persona is None:
            self.character_persona = (
                f"You are {character_name}, a helpful and friendly NQU AI assistant. "
                f"You are cheerful, supportive, and always ready to help. "
                f"Keep your responses concise and natural, as if speaking in a conversation. "
                f"You can help with information, answer questions, or just chat."
                f"give me short answer."
            )
        else:
            self.character_persona = character_persona

        logger.info(f"OpenRouter client initialized with model {self.model}")

    def generate_response(
        self,
        prompt: str,
        conversation_history: List[Dict[str, str]] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate a response using OpenRouter.

        Args:
            prompt: User prompt
            conversation_history: Previous conversation messages
            system_prompt: Optional system prompt to override the default

        Returns:
            Generated response text
        """
        try:
            # Prepare messages
            messages = []

            # Add system message
            if system_prompt is None:
                system_prompt = self.character_persona

            messages.append({"role": "system", "content": system_prompt})

            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Limit to last 10 messages
                print(messages)

            # Add user prompt if not already in history
            if not conversation_history or conversation_history[-1]["role"] != "user":
                messages.append({"role": "user", "content": prompt})
                print(messages)

            # Prepare request headers and data
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }

            # Make the API request
            response = requests.post(self.api_url, headers=headers, json=data)
            print(response.text)

            # Check for successful response
            response.raise_for_status()

            # Parse response
            result = response.json()

            # Extract the response text
            if "choices" in result and len(result["choices"]) > 0:
                if (
                    "message" in result["choices"][0]
                    and "content" in result["choices"][0]["message"]
                ):
                    return result["choices"][0]["message"]["content"]

            # If we couldn't extract the response content
            logger.warning(f"Unexpected response format: {result}")
            return "I'm sorry, I couldn't process your request properly."

        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            return "I'm sorry, I encountered a network error. Please try again later."
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return "I'm sorry, I received an invalid response format. Please try again later."
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error. Please try again later."

    def generate_emotion_response(self, emotion: str) -> str:
        """
        Generate a response based on detected emotion.

        Args:
            emotion: Detected emotion (e.g., "happy", "sad", "angry")

        Returns:
            Generated response text
        """
        emotion_prompts = {
            "happy": "The user looks happy. Respond in a cheerful way, matching their positive mood.",
            "sad": "The user looks sad. Respond with empathy and ask if they're okay.",
            "angry": "The user looks upset. Respond calmly and ask if something is bothering them.",
            "surprise": "The user looks surprised. Respond with curiosity about what surprised them.",
            "fear": "The user looks worried or scared. Respond with reassurance and offer support.",
            "disgust": "The user looks disgusted. Respond with concern and ask what's wrong.",
            "neutral": "The user has a neutral expression. Respond normally and perhaps ask how they're doing.",
        }

        # Get the appropriate prompt for the emotion, or use a default
        prompt = emotion_prompts.get(
            emotion,
            f"Respond to the user naturally, considering they appear {emotion}.",
        )

        # Generate and return response
        return self.generate_response(prompt, [])
