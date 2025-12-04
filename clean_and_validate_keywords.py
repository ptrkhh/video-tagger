import re


def clean_and_validate_keywords(text: str) -> str:
    text = re.sub(r'["\[\]\n\r\t]', ' ', text)
    text = re.sub(r'[<>:"/\\|?*]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text
