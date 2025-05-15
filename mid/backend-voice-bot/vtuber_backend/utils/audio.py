#!/usr/bin/env python3
"""
Audio utilities for the VTuber backend.
"""
import base64
import logging
import os

logger = logging.getLogger(__name__)


def encode_audio_to_base64(audio_path: str) -> str:
    """
    Encode audio file to base64.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Base64-encoded audio data
    """
    try:
        with open(audio_path, 'rb') as audio_file:
            audio_data = audio_file.read()
            return base64.b64encode(audio_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding audio to base64: {e}")
        raise


def decode_base64_to_audio(base64_data: str, output_path: str) -> str:
    """
    Decode base64 data to audio file.
    
    Args:
        base64_data: Base64-encoded audio data
        output_path: Path to save the audio file
        
    Returns:
        Path to the saved audio file
    """
    try:
        audio_data = base64.b64decode(base64_data)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        with open(output_path, 'wb') as audio_file:
            audio_file.write(audio_data)
        return output_path
    except Exception as e:
        logger.error(f"Error decoding base64 to audio: {e}")
        raise
