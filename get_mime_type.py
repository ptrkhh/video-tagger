from pathlib import Path


def get_mime_type(file_path: Path) -> str:
    file_extension = file_path.suffix.lower()

    # Video MIME types
    if file_extension in ['.mp4', '.avi', '.mov', '.webm']:
        return f"video/{file_extension[1:]}"

    if file_extension == '.jpg' or file_extension == '.jpeg':
        return "image/jpeg"
    elif file_extension == '.png':
        return "image/png"
    elif file_extension == '.webp':
        return "image/webp"
    elif file_extension == '.heic':
        return "image/heic"
    else:
        return f"image/{file_extension[1:]}"
