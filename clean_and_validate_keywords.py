import re


def clean_and_validate_keywords(text: str) -> str:
    text_without_structural_chars = re.sub(r'["\[\]\n\r\t]', ' ', text)
    text_without_invalid_chars = re.sub(r'[<>:"/\\|?*]', ' ', text_without_structural_chars)
    text_normalized = re.sub(r'\s+', ' ', text_without_invalid_chars).strip()

    return text_normalized
