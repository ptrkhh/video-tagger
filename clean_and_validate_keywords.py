"""
Clean and validate keywords from AI-generated text.

The AI generates descriptive text that needs to be cleaned before
using it as a filename. This removes invalid filename characters
and normalizes whitespace.
"""

import re


def clean_and_validate_keywords(text: str) -> str:
    """
    Clean AI-generated text to make it safe for use in filenames.

    Removes or replaces characters that are invalid in filenames
    across different operating systems (Windows, Mac, Linux).

    Args:
        text: Raw text from the AI model

    Returns:
        Cleaned text suitable for use in a filename

    Examples:
        >>> clean_and_validate_keywords('Hello "World"\\nNew Line')
        'Hello  World  New Line'
        >>> clean_and_validate_keywords('File<name>with:invalid*chars')
        'File name with invalid chars'
    """
    # Remove quotes, brackets, and whitespace control characters
    text_without_structural_chars = re.sub(r'["\[\]\n\r\t]', ' ', text)

    # Remove characters that are invalid in filenames
    # These are: < > : " / \ | ? *
    text_without_invalid_chars = re.sub(r'[<>:"/\\|?*]', ' ', text_without_structural_chars)

    # Collapse multiple spaces into single space and trim whitespace from ends
    text_normalized = re.sub(r'\s+', ' ', text_without_invalid_chars).strip()

    return text_normalized
