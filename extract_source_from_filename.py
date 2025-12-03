import time
from typing import Optional

from google.genai import Client
from google.genai.types import GenerateContentConfig

import config


def extract_username_from_filename(filename: str) -> Optional[str]:
    if not filename or not filename.strip():
        return None

    for attempt in range(3):
        try:
            # Add rate limiting delay
            if attempt > 0:
                wait_time = 2 * (2 ** attempt)  # Exponential backoff: 4s, 8s
                print(f"  Retrying source extraction in {wait_time}s (attempt {attempt + 1}/3)...")
                time.sleep(wait_time)
            else:
                time.sleep(0.5)  # Small delay to respect rate limits

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
                    max_output_tokens=20,
                    top_p=1.0,
                    top_k=1
                )
            )

            # Validate and extract text from response
            if not response:
                raise ValueError("Response is None")

            if not hasattr(response, 'candidates') or not response.candidates:
                if hasattr(response, 'prompt_feedback'):
                    raise ValueError(f"No candidates. Prompt feedback: {response.prompt_feedback}")
                raise ValueError("No candidates in response")

            candidate = response.candidates[0]

            # Check for blocked content
            if hasattr(candidate, 'finish_reason'):
                finish_reason = str(candidate.finish_reason)
                if 'SAFETY' in finish_reason or 'BLOCKED' in finish_reason:
                    raise ValueError(f"Content blocked: {finish_reason}")

            if not hasattr(candidate, 'content') or not candidate.content:
                raise ValueError(f"No content in candidate")

            if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                raise ValueError("No parts in content")

            part = candidate.content.parts[0]
            if not hasattr(part, 'text') or not part.text:
                raise ValueError("No text in part")

            extracted_text = part.text.strip()

            if extracted_text.lower() == "none":
                return ""
            return extracted_text

        except Exception as e:
            print(f"  ⚠️  Error extracting source from filename (attempt {attempt + 1}/3): {e}")

    print(f"  ⚠️  Failed to extract source using AI after 3 attempts, falling back to simple extraction")

    # Fallback: simple first-word extraction
    words = filename.replace('-', ' ').replace('_', ' ').replace('202', ' ').split()
    if words:
        first_word = words[0]
        if first_word.lower() not in config.application_config.generic_source_keywords:
            return first_word

    return None
