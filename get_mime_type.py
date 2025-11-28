"""
Determine MIME types for media files.

MIME types are used by the AI API to understand what type of file
is being sent for analysis.
"""

from pathlib import Path


def get_mime_type(file_path: Path) -> str:
    """
    Determine the proper MIME type for a media file.

    MIME types tell the API what kind of file is being processed.
    This is required for the Gemini API to properly analyze the file.

    Args:
        file_path: Path object pointing to the media file

    Returns:
        MIME type string (e.g., "video/mp4", "image/jpeg")

    Examples:
        >>> get_mime_type(Path("video.mp4"))
        "video/mp4"
        >>> get_mime_type(Path("photo.jpg"))
        "image/jpeg"
    """
    file_extension = file_path.suffix.lower()

    # Video MIME types
    if file_extension in ['.mp4', '.avi', '.mov', '.webm']:
        # Remove the leading dot from extension for MIME type
        return f"video/{file_extension[1:]}"

    # Image MIME types with special cases
    if file_extension == '.jpg' or file_extension == '.jpeg':
        return "image/jpeg"
    elif file_extension == '.png':
        return "image/png"
    elif file_extension == '.webp':
        return "image/webp"
    elif file_extension == '.heic':
        return "image/heic"
    else:
        # Default to image MIME type for unknown extensions
        return f"image/{file_extension[1:]}"
