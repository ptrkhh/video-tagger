import time
from pathlib import Path

from google.genai import Client
from google.genai.types import Part, GenerateContentConfig

import config
from get_mime_type import get_mime_type


def analyze_media_content(file_path: Path):

    prompt = """
Generate STRATEGIC search keywords for this automotive media.

CRITICAL REQUIREMENT: Your response MUST be between 200-400 characters. This is a strict requirement.

FOCUS ON:
1. Brand/model identification (use common abbreviations/nicknames)
2. Key distinguishing features (1-3 terms max)
3. Content type (only if not obvious): meme, review, comparison, accident
4. Selective bilingual (pick most searchable term per concept, not both)
5. Local slang when relevant (mercy=Mercedes, mobcin=Chinese car)

AVOID:
- Exhaustive synonym lists
- Redundant translations
- Repetitive descriptors
- Long narratives

EXAMPLES (note the length - aim for similar):
• Meme about Mercedes fuel consumption: "mercedes w211 eclass bbm boros fuel consumption dashboard comparison meme funny expensive maintenance costs reliability german engineering luxury sedan"
• Audi with Sonic sticker: "audi sonic sticker modifikasi custom funny creative automotive humor pop culture reference blue hedgehog sega gaming crossover unexpected modification quirky"
• License plate math pun: "license plate plat nomor multiplication perkalian math pun helpful educational clever wordplay indonesia traffic humor mathematical joke creative license plate design unique"
• Mazda vs Wuling comparison: "mazda cx5 wuling almaz comparison suv saling nyindir meme rivalry brand comparison japanese indonesian automotive market competition price value features specification review"

FORMAT: Space-separated lowercase keywords. Generate enough keywords to reach 150-400 characters total.

Count your output to ensure it meets the 150-400 character requirement before responding.

Now analyze this media and generate strategic keywords:
    """
    client = Client(
        location=config.application_config.gcp_region,
        project=config.application_config.gcp_project_id,
        vertexai=True,
    )

    # Read file content and create Part using from_bytes for Vertex AI
    with open(file_path, 'rb') as f:
        file_data = f.read()

    mime_type = get_mime_type(file_path)
    media_part = Part.from_bytes(data=file_data, mime_type=mime_type)

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            # Add rate limiting delay to avoid hitting API limits
            if attempt > 0:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                print(f"  Retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                # Small delay even on first attempt to respect rate limits
                time.sleep(1)

            response = client.models.generate_content(
                model=config.application_config.model_name,
                contents=[media_part, prompt],
                config=GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=500,
                    top_p=0.95,
                    top_k=40
                )
            )

            # Validate response immediately after getting it
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
                    raise ValueError(f"Content blocked by safety filters: {finish_reason}")

            if not hasattr(candidate, 'content') or not candidate.content:
                raise ValueError(f"No content in candidate. Finish reason: {getattr(candidate, 'finish_reason', 'unknown')}")

            if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                raise ValueError("No parts in response content")

            part = candidate.content.parts[0]
            if not hasattr(part, 'text') or not part.text:
                raise ValueError("No text in response part")

            response_text = part.text.strip()
            if len(response_text) < 80:
                raise ValueError(f"Response too short ({len(response_text)} chars), retrying...")

            # Success - return the response
            return response

        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                print(f"  ⚠️  Attempt {attempt + 1} failed: {error_msg}")
            else:
                # Last attempt failed
                raise ValueError(f"API call failed after {max_retries} attempts: {error_msg}")

    # Should never reach here, but just in case
    raise ValueError(f"API call failed after {max_retries} attempts")
