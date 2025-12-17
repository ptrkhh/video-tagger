from dataclasses import dataclass
from typing import ClassVar

from google.genai import Client


@dataclass
class Config:
    input_directory: str = "input"
    output_directory: str = "output"

    gcp_project_id: str = "ubm-gen-ai"
    gcp_credentials_path: str = "credentials/gsa.json"

    model_name: str = "gemini-3-pro-preview"
    prompt_file_path: str = "prompt.txt"
    use_ai_to_get_username: bool = True

    max_workers: int = 1

    maximum_file_size_mb: int = 100

    filename_target_minimum_length: int = 230
    filename_target_maximum_length: int = 250

    filename_absolute_maximum_length: int = 255

    maximum_retry_attempts: int = 3
    retry_minimum_wait_seconds: int = 2
    retry_maximum_wait_seconds: int = 30

    minimum_response_length_characters: int = 80
    maximum_response_length_characters: int = 200

    supported_video_extensions: ClassVar[list[str]] = [".mp4", ".avi", ".mov", ".webm"]
    supported_image_extensions: ClassVar[list[str]] = [".jpg", ".jpeg", ".png", ".heic", ".webp"]

    generic_source_keywords: ClassVar[list[str]] = ["img", "image", "pic", "photo", "video", "vid", "screenshot"]

    client = Client(
        location="global",
        project=gcp_project_id,
        vertexai=True,
    )
    client_us_central_1 = Client(
        location="us-central1",
        project=gcp_project_id,
        vertexai=True,
    )


    def get_all_supported_media_extensions(self) -> list[str]:
        return self.supported_video_extensions + self.supported_image_extensions


application_config = Config()
