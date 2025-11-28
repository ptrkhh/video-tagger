"""
Functions for processing individual media files.

This module contains utilities for analyzing and renaming media files
based on AI-generated keywords.
"""

import os
from pathlib import Path
from typing import Callable

from analyze_media_content import analyze_media_content
from build_filename import build_filename
from clean_and_validate_keywords import clean_and_validate_keywords
from config import application_config
from extract_source_from_filename import extract_username_from_filename
from get_mime_type import get_mime_type

from vertexai.generative_models import GenerativeModel, Part

def generate_new_filename(original_path: Path, gemini_response: str) -> str:
    """
    Generate a new filename based on AI analysis.

    Args:
        original_path: The original file path
        gemini_response: The AI-generated analysis text

    Returns:
        A new filename with source, keywords, and original extension
    """
    source = extract_username_from_filename(original_path.name)
    keywords = clean_and_validate_keywords(gemini_response)
    new_filename = build_filename(source, keywords, original_path.suffix)

    return new_filename


def process_single_file(file_path: Path, analyze_func: Callable[[Path], str]) -> bool:
    try:
        print(f"Processing: {file_path.name}")

        file_bytes = file_path.read_bytes()
        file_mime_type = get_mime_type(file_path)
        media_part = Part.from_data(data=file_bytes,mime_type=file_mime_type)

        response = analyze_media_content(media_part)
        if not response or not response.text:
            raise ValueError("Gemini returned no response")

        response_text = response.text.strip()

        minimum_length = application_config.minimum_response_length_characters
        if len(response_text) < minimum_length:
            raise ValueError(
                f"Gemini response too short ({len(response_text)} chars, "
                f"minimum {minimum_length}): {response_text}"
            )

        maximum_length = application_config.maximum_response_length_characters
        if len(response_text) > maximum_length:
            print(f"  ⚠️  Response very long ({len(response_text)} chars), "
                  f"may be truncated in filename")

        print(f"Keywords generated for {file_path.name}: {len(ai_analysis)} chars")

        # Show a preview of the analysis
        preview_length = 150
        if len(ai_analysis) > preview_length:
            preview = ai_analysis[:preview_length] + '...'
        else:
            preview = ai_analysis
        print(f"Preview for {file_path.name}: {preview}")

        # Generate new filename from AI analysis
        new_filename = generate_new_filename(file_path, ai_analysis)
        new_file_path = Path(application_config.output_directory) / new_filename

        # Handle filename collisions by adding a counter
        if new_file_path.exists():
            collision_counter = 1
            while new_file_path.exists():
                # Use os.path.splitext to properly split filename and extension
                base_filename, file_extension = os.path.splitext(new_filename)
                new_filename = f"{base_filename} ({collision_counter}){file_extension}"
                new_file_path = Path(application_config.output_directory) / new_filename
                collision_counter += 1
            print(f"  File exists, using: {new_filename}")

        # Move file to output directory with new name
        file_path.rename(new_file_path)
        print(f"✓ Renamed {file_path.name} --> {new_filename}")

        return True

    except Exception as error:
        print(f"\n✗ Error processing {file_path.name}: {error}\n")
        return False
