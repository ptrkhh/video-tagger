import os
from typing import Optional
from config import application_config


def build_filename(source: Optional[str], keywords: str, extension: str) -> str:
    base_filename = ' '.join([source if source else "", keywords if keywords else ""])
    maximum_base_length = application_config.filename_absolute_maximum_length - len(extension)

    if len(base_filename) > maximum_base_length:
        base_filename = truncate_at_word_boundary(base_filename, maximum_base_length)
        print(f"  ⚠️  Truncated from {len(base_filename)} to {len(base_filename)} chars")
    elif len(base_filename) < application_config.filename_target_minimum_length:
        print(f"  ⚠️  Only {len(base_filename)} chars - below target of {application_config.filename_target_minimum_length}")
    return base_filename + extension


def truncate_at_word_boundary(text: str, maximum_length: int) -> str:
    while len(text) > maximum_length:
        text = " ".join(text.split(" ")[:-1])
    return text
