"""
Build filenames from source and keyword components.

Creates filenames that are descriptive, searchable, and filesystem-compatible.
Handles truncation intelligently when filenames exceed system limits.
"""

import os
from typing import Optional
from config import application_config


def build_filename(source: Optional[str], keywords: str, extension: str) -> str:
    """
    Build a filename from source identifier, keywords, and file extension.

    Combines the source (e.g., "Instagram") and AI-generated keywords into
    a single filename. Ensures the filename fits within filesystem limits
    while preserving as much information as possible.

    Args:
        source: Source identifier (e.g., "Instagram", "Camera"), or None
        keywords: Descriptive keywords from AI analysis
        extension: File extension including the dot (e.g., ".jpg", ".mp4")

    Returns:
        Complete filename including extension

    Examples:
        >>> build_filename("Instagram", "sunset beach photo", ".jpg")
        "Instagram sunset beach photo.jpg"
        >>> build_filename(None, "cat playing piano", ".mp4")
        "cat playing piano.mp4"
    """
    # Collect all filename components that are not empty
    filename_components = []
    if source:
        filename_components.append(source)
    if keywords:
        filename_components.append(keywords)

    # Join components with spaces
    base_filename = ' '.join(filename_components)

    # Calculate how much space we have for the base filename
    # (filesystem limit minus the extension length)
    maximum_base_length = application_config.filename_absolute_maximum_length - len(extension)
    current_base_length = len(base_filename)

    # Check if truncation is needed
    if current_base_length > maximum_base_length:
        original_length = current_base_length
        base_filename = _truncate_at_word_boundary(base_filename, maximum_base_length)
        characters_lost = original_length - len(base_filename)
        print(f"  ⚠️  Truncated from {original_length} to {len(base_filename)} chars "
              f"({characters_lost} chars lost due to filesystem limit)")

    elif current_base_length < application_config.filename_target_minimum_length:
        print(f"  ⚠️  Only {current_base_length} chars - below target of "
              f"{application_config.filename_target_minimum_length}")

    elif (application_config.filename_target_minimum_length <= current_base_length
          <= application_config.filename_target_maximum_length):
        print(f"  ✓ {current_base_length} chars - good length")

    return base_filename + extension


def _truncate_at_word_boundary(text: str, maximum_length: int) -> str:
    """
    Truncate text at a word boundary to avoid cutting words in half.

    If truncating at a word boundary would lose too much text (more than 10%),
    falls back to simple character truncation.

    Args:
        text: Text to truncate
        maximum_length: Maximum length in characters

    Returns:
        Truncated text, trimmed of whitespace

    Examples:
        >>> _truncate_at_word_boundary("hello world example", 12)
        "hello world"  # Truncates at word boundary
        >>> _truncate_at_word_boundary("verylongwordhere", 10)
        "verylongwo"  # Falls back to character truncation
    """
    # First, truncate to the maximum length
    truncated_text = text[:maximum_length]

    # Find the last space in the truncated text
    last_space_position = truncated_text.rfind(' ')

    # Calculate the threshold: we don't want to lose more than 10% of allowed length
    minimum_acceptable_length = maximum_length * 0.9

    # Use word boundary if we found a space and it's not too far back
    if last_space_position > minimum_acceptable_length:
        return truncated_text[:last_space_position].strip()
    else:
        # Fall back to character truncation if word boundary is too far back
        return truncated_text.strip()
