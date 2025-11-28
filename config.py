"""
Centralized configuration for the Media Tagger application.

This module contains all configuration constants used throughout the application.
Using a centralized config makes the code easier to understand, test, and modify.
"""

import os
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class Config:
    """
    Application configuration with sensible defaults.

    All configuration values are stored here to make them easy to find and modify.
    Values can be overridden by environment variables.
    """

    # Directory paths for input and output files
    input_directory: str = "input"
    output_directory: str = "output"

    # Google Cloud Platform settings
    gcp_project_id: str = "ubm-gen-ai"
    gcp_region: str = "us-central1"
    gcp_credentials_path: str = "credentials/ubm-gen-ai-gsa.json"

    # AI model configuration
    model_name: str = "gemini-2.5-flash"
    prompt_file_path: str = "prompt.txt"

    # Concurrent processing configuration
    # Note: Reduced from 10 to 5 to avoid API rate limits
    maximum_concurrent_workers: int = 5

    # File size limits (in megabytes)
    maximum_file_size_mb: int = 100

    # Filename length constraints (in characters)
    # Target range for optimal filename length
    filename_target_minimum_length: int = 230
    filename_target_maximum_length: int = 250

    # Absolute maximum length imposed by filesystem
    filename_absolute_maximum_length: int = 255

    # Retry configuration for API calls
    maximum_retry_attempts: int = 3
    retry_minimum_wait_seconds: int = 2
    retry_maximum_wait_seconds: int = 30

    # Response validation
    minimum_response_length_characters: int = 10
    maximum_response_length_characters: int = 500

    # Supported file extensions
    supported_video_extensions: ClassVar[list[str]] = [".mp4", ".avi", ".mov", ".webm"]
    supported_image_extensions: ClassVar[list[str]] = [".jpg", ".jpeg", ".png", ".heic", ".webp"]

    # Words to filter out from source extraction
    generic_source_keywords: ClassVar[list[str]] = [
        "img", "image", "pic", "photo", "video", "vid", "screenshot"
    ]

    @classmethod
    def from_environment(cls) -> 'Config':
        """
        Create a Config instance from environment variables.

        Environment variables override default values.
        This makes the application configurable without code changes.

        Returns:
            Config instance with values from environment or defaults
        """
        return cls(
            input_directory=os.getenv('INPUT_DIR', cls.input_directory),
            output_directory=os.getenv('OUTPUT_DIR', cls.output_directory),
            gcp_project_id=os.getenv('GCP_PROJECT', cls.gcp_project_id),
            gcp_region=os.getenv('GCP_LOCATION', cls.gcp_region),
            gcp_credentials_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS', cls.gcp_credentials_path),
            model_name=os.getenv('MODEL_NAME', cls.model_name),
            maximum_concurrent_workers=int(os.getenv('MAX_WORKERS', str(cls.maximum_concurrent_workers))),
        )

    def get_all_supported_media_extensions(self) -> list[str]:
        """
        Get a combined list of all supported media file extensions.

        Returns:
            List of file extensions including the leading dot (e.g., [".mp4", ".jpg"])
        """
        return self.supported_video_extensions + self.supported_image_extensions


# Global configuration instance that can be imported by other modules
application_config = Config.from_environment()
