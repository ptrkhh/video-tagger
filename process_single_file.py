import os
from pathlib import Path

from tqdm import tqdm

from analyze_media_content import analyze_media_content
from build_filename import build_filename
from clean_and_validate_keywords import clean_and_validate_keywords
from config import application_config
from extract_username_from_filename import extract_username_from_filename


def generate_new_filename(original_path: Path, gemini_response: str) -> str:
    source = extract_username_from_filename(original_path.name)
    tqdm.write(f"  Source: {source}")
    keywords = clean_and_validate_keywords(gemini_response)
    tqdm.write(f"  Keywords: {keywords}")
    new_filename = build_filename(source, keywords, original_path.suffix)
    return new_filename


def process_single_file(file_path: Path) -> bool:
    try:
        tqdm.write(f"Processing: {file_path.name}")
        response = analyze_media_content(file_path)
        if not response or not response.text:
            raise ValueError("Gemini returned no response")
        response = response.text.strip()

        minimum_length = application_config.minimum_response_length_characters
        if len(response) < minimum_length:
            raise ValueError(
                f"Gemini response too short ({len(response)} chars, "
                f"minimum {minimum_length}): {response}"
            )

        tqdm.write(f"Keywords generated for {file_path.name}: {len(response)} chars")

        preview_length = 100
        preview = response[:preview_length] + '...' if len(response) > preview_length else response
        tqdm.write(f"Preview for {file_path.name}: {preview}")

        new_filename = generate_new_filename(file_path, response)
        new_file_path = Path(application_config.output_directory) / new_filename

        if new_file_path.exists():
            collision_counter = 1
            while new_file_path.exists():
                base_filename, file_extension = os.path.splitext(new_filename)
                new_filename = f"{base_filename} ({collision_counter}){file_extension}"
                new_file_path = Path(application_config.output_directory) / new_filename
                collision_counter += 1
            tqdm.write(f"  File exists, using: {new_filename}")

        file_path.rename(new_file_path)
        tqdm.write(f"✓ Renamed {file_path.name} --> {new_filename}")

        return True

    except Exception as error:
        tqdm.write(f"\n✗ Error processing {file_path.name}: {error}\n")
        return False
