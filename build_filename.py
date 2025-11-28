import os
from typing import Optional
from config import application_config


def build_filename(source: Optional[str], keywords: str, extension: str) -> str:
    filename_components = []
    if source:
        filename_components.append(source)
    if keywords:
        filename_components.append(keywords)

    base_filename = ' '.join(filename_components)

    maximum_base_length = application_config.filename_absolute_maximum_length - len(extension)
    current_base_length = len(base_filename)

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
    truncated_text = text[:maximum_length]
    last_space_position = truncated_text.rfind(' ')
    minimum_acceptable_length = maximum_length * 0.9
    if last_space_position > minimum_acceptable_length:
        return truncated_text[:last_space_position].strip()
    else:
        return truncated_text.strip()
