import time
from pathlib import Path

from google.genai.types import Part, GenerateContentConfig

import config
from get_mime_type import get_mime_type


def analyze_media_content(file_path: Path):
    system_instruction = """
ROLE: You are an automated file archivist for an automotive media library.

OBJECTIVE: Generate a single string of space-separated keywords to be used as a filename. You MUST fill the filename buffer (target: 230-254 characters) with the most likely search terms.

CRITICAL CONSTRAINTS:

NO CONVERSATION: Do not write "Here are the keywords." Do not use "sure." Do not use markdown code blocks. Start directly with the first keyword. Any extra text will break the script.

TRANSCRIPTION (OCR): If the image contains text (titles, subtitles, memes, stickers), you must include it.

OUTPUT FORMAT: Lowercase, space-separated only. NO punctuation, NO file extensions.

LENGTH: Strictly 230-254 characters.
    """

    prompt = """
CRITICAL "GREP" RULES:

Substring Exclusion: Strictly check for redundancy. If a word is a substring of a longer word, omit the shorter word.
  - If you include "kecelakaan", DO NOT include "celaka"
  - If you include "racing", DO NOT include "race"
  - If you include "automotive", DO NOT include "auto"

Synonym Stacking: Include distinct synonyms (English, Indonesian, Slang) to maximize search hits.
  - good: "crash nabrak collision"
  - good: "boros wasteful pemborosan"

Priority Sorting: Most important keywords (Brand, Model, Main Event) must come first. Lower priority descriptors go last.

CONTENT PRIORITY:
1. Identity: Brand, Model, Chassis Code (e.g., w204, g20), common nicknames (e.g., mobcin, mercy)
2. Action/Genre: Review, crash, drag race, meme, funny
3. Visible Text/Title: Transcription of any text in the image
4. Distinct Synonyms: (e.g., "boros" + "wasteful", "kencang" + "fast")
5. Context: Location (if relevant), specific modification parts (e.g., turbo, spoiler)

EXAMPLES (Follow this density):

Input: A thumbnail with text "CIVIC TURBO LAWAN XPENDER!!"
Output: honda civic turbo fk8 vs mitsubishi xpander cross drag race adu mekanik lawan rivalry fwd battle acceleration kencang fast speed tuning modifikasi mpv sedan hatchback jdm funny judul clickbait thumbnail text viral trending youtube indonesia

Input: A photo of a Suzuki Jimny with a "4x4 Life" sticker mudding
Output: suzuki jimny jb74 katana sierra 4x4 life sticker decal offroad lumpur mudding stuck kepater recovery winch arb forest hutan adventure camping overland mini jeep kei car legendary ladder frame solid axle suspension lift kit modification accessories

Input: Meme text "Me waiting for parts"
Output: me waiting for parts text caption meme funny relatable sparepart onderdil lama shipping delay project car builds unfinished jackstand bengkel garage mechanic pain suffering patience import customs bea cukai tax mahal expensive hobby automotive enthusiast struggle

ANALYZE THIS MEDIA AND OUTPUT KEYWORDS:
    """

    with open(file_path, 'rb') as f:
        file_data = f.read()

    mime_type = get_mime_type(file_path)
    media_part = Part.from_bytes(data=file_data, mime_type=mime_type)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = config.application_config.client.models.generate_content(
                model="gemini-3-pro-preview",
                contents=[media_part, prompt],
                config=GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=1000,
                    top_p=0.95,
                    top_k=40,
                    system_instruction=system_instruction
                )
            )

            if not response:
                raise ValueError("Response is None")

            if not hasattr(response, 'text') or not response.text:
                if not hasattr(response, 'candidates') or not response.candidates:
                    if hasattr(response, 'prompt_feedback'):
                        raise ValueError(f"No candidates. Prompt feedback: {response.prompt_feedback}")
                    raise ValueError("No candidates in response")

                candidate = response.candidates[0]

                if hasattr(candidate, 'finish_reason'):
                    finish_reason = str(candidate.finish_reason)
                    if 'SAFETY' in finish_reason or 'BLOCKED' in finish_reason:
                        raise ValueError(f"Content blocked by safety filters: {finish_reason}")

                if not hasattr(candidate, 'content') or not candidate.content:
                    raise ValueError(
                        f"No content in candidate. Finish reason: {getattr(candidate, 'finish_reason', 'unknown')}")

                raise ValueError("No text in response")

            response_text = response.text.strip()
            if len(response_text) < 80:
                raise ValueError(f"Response too short ({len(response_text)} chars), retrying...")
            return response

        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                print(f"  ⚠️  Attempt {attempt + 1} failed: {error_msg}")
            else:
                raise ValueError(f"API call failed after {max_retries} attempts: {error_msg}")

    raise ValueError(f"API call failed after {max_retries} attempts")
