from typing import Optional

from google.genai import Client
from google.genai.types import GenerateContentConfig

import config


def extract_username_from_filename(filename: str) -> Optional[str]:
    if not filename or not filename.strip():
        return None

    for attempt in range(3):
        try:
            prompt = f"""
Extract the username from this filename: '{filename}'

The username is an Instagram/TikTok/Twitter handle such as indonesia_speed, indra_fathan, info.bsd.gadingserpong, infodepok_id, jakarta.terkini, jay_scotch_autos, jonathanch6506, jmotorhaus, makecaradsgreatagain, sekenauto.

Rules:
- Return ONLY the username
- If the filename does not contain a username, return "NONE"
- Do not include any explanation, punctuation, or extra text

Username:
"""

            client = Client(
                location=config.application_config.gcp_region,
                project=config.application_config.gcp_project_id,
                vertexai=True,
            )
            response = client.models.generate_content(
                model=config.application_config.model_name,
                contents=[prompt],
                config=GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=5,
                    top_p=1.0,
                    top_k=1
                )
            )
            response = response.candidates[0].content.parts[0].text.strip()
            if response.lower() == "none":
                return ""
            return response

        except Exception as e:
            print(f"  ⚠️  Error extracting source from filename (attempt {attempt + 1}/3): {e}")

    print(f"  ⚠️  Failed to extract source using AI after 3 attempts, falling back to simple extraction")

    # Fallback: simple first-word extraction
    words = filename.replace('-', ' ').replace('_', ' ').split()
    if words:
        first_word = words[0]
        if first_word.lower() not in config.application_config.generic_source_keywords:
            return first_word

    return None
