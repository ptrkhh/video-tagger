"""
Media Tagger - Automatically tag and rename media files using AI.

This application uses Google's Gemini AI to analyze images and videos,
generate descriptive keywords, and rename files with searchable,
meaningful names.
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

import vertexai
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tqdm import tqdm
from vertexai.generative_models import GenerativeModel, Part

from analyze_media_content import analyze_media_content
from config import application_config
from get_mime_type import get_mime_type
from process_single_file import process_single_file


# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = application_config.gcp_credentials_path

# Initialize Vertex AI with project and location
vertexai.init(
    project=application_config.gcp_project_id,
    location=application_config.gcp_region
)


class MediaTagger:
    def __init__(self) -> None:
        self.input_directory = Path(application_config.input_directory)
        self.output_directory =

        self.output_directory.mkdir(exist_ok=True)
        self.maximum_workers = application_config.maximum_concurrent_workers

    @retry(
        stop=stop_after_attempt(application_config.maximum_retry_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=application_config.retry_minimum_wait_seconds,
            max=application_config.retry_maximum_wait_seconds
        ),
        retry=retry_if_exception_type((ResourceExhausted, ServiceUnavailable)),
        reraise=True
    )

    def process_media(self) -> None:
        """
        Process all media files in the input directory.

        Finds all supported media files, processes them concurrently with
        a thread pool, and displays progress. Each file is analyzed with AI
        and renamed based on its content.
        """
        # Get all supported media file extensions from config
        supported_extensions = application_config.get_all_supported_media_extensions()

        # Find all media files in the input directory
        media_files = [
            file for file in self.input_directory.glob("*")
            if file.suffix.lower() in supported_extensions and file.is_file()
        ]

        # Exit early if no files found
        if not media_files:
            print("No media files found in input directory.")
            return

        # Display summary of what will be processed
        print(f"\nFound {len(media_files)} media files to process.")
        print(f"Target filename length: "
              f"{application_config.filename_target_minimum_length}-"
              f"{application_config.filename_target_maximum_length} characters")
        print(f"Processing with {self.maximum_workers} workers...\n")

        # Track success and failure counts
        success_count = 0
        fail_count = 0

        # Process files concurrently with thread pool
        with ThreadPoolExecutor(max_workers=self.maximum_workers) as executor:
            # Submit all files for processing
            futures = {
                executor.submit(process_single_file, file_path): file_path
                for file_path in media_files
            }

            # Process results as they complete, with progress bar
            with tqdm(total=len(media_files), desc="Processing files", unit="file") as progress_bar:
                for future in as_completed(futures):
                    file_path = futures[future]

                    try:
                        # Check if the future raised an exception
                        exception = future.exception()
                        if exception:
                            print(f"\n✗ Exception processing {file_path.name}: {exception}\n")
                            fail_count += 1
                        elif future.result():
                            # File processed successfully
                            success_count += 1
                        else:
                            # File processing returned False (handled error)
                            fail_count += 1

                    except Exception as error:
                        # Catch any unexpected errors when retrieving the result
                        print(f"\n✗ Unexpected error retrieving result for {file_path.name}: {error}\n")
                        fail_count += 1

                    finally:
                        # Update progress bar regardless of outcome
                        progress_bar.update(1)
                        progress_bar.set_postfix({
                            'success': success_count,
                            'failed': fail_count
                        })

        # Display final summary
        separator_line = '=' * 80
        print(f"\n{separator_line}")
        print(f"Processing complete!")
        print(f"Success: {success_count} | Failed: {fail_count} | Total: {len(media_files)}")
        print(f"{separator_line}\n")


if __name__ == '__main__':
    tagger = MediaTagger()
    tagger.process_media()
