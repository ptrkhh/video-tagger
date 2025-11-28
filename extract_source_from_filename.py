from typing import Optional

from vertexai.generative_models import GenerativeModel, GenerationConfig

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

            model = GenerativeModel("gemini-2.5-flash-lite")
            response = model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=10,
                    top_p=1.0,
                    top_k=1
                )
            )

            result = response.text.strip()
            if result.lower() == "none":
                return ""
            return result

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
