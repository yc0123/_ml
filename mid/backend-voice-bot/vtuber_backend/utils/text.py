#!/usr/bin/env python3
"""
Text utilities for the VTuber backend.
"""
import logging

logger = logging.getLogger(__name__)


def get_language_code(text: str) -> str:
    """
    Attempt to detect the language of the text.
    This is a simple heuristic-based approach.
    
    Args:
        text: Text to detect language for
        
    Returns:
        Language code ('zh' for Chinese, 'en' for English, etc.)
    """
    # Check for Chinese characters
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return 'zh'
    
    # Default to English
    return 'en'


def sanitize_text(text: str) -> str:
    """
    Sanitize text for TTS processing.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Replace special characters that might cause issues
    replacements = {
        '&': ' and ',
        '<': ' less than ',
        '>': ' greater than ',
        '...': '.',
        '--': '-',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text
