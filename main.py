import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from config import application_config
from process_single_file import process_single_file

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = application_config.gcp_credentials_path


class MediaTagger:
    def __init__(self) -> None:
        Path(application_config.output_directory).mkdir(exist_ok=True)

    # @retry(
    #     stop=stop_after_attempt(application_config.maximum_retry_attempts),
    #     wait=wait_exponential(multiplier=1, min=application_config.retry_minimum_wait_seconds, max=application_config.retry_maximum_wait_seconds),
    #     retry=retry_if_exception_type((ResourceExhausted, ServiceUnavailable)),
    #     reraise=True
    # )
    def process_media(self) -> None:
        supported_extensions = application_config.get_all_supported_media_extensions()
        media_files = [f for f in Path(application_config.input_directory).glob("*") if
                       f.suffix.lower() in supported_extensions and f.is_file()]

        if not media_files:
            print("No media files found in input directory.")
            return

        print(f"\nFound {len(media_files)} media files to process.")
        print(f"Target filename length: {application_config.filename_target_minimum_length}-{application_config.filename_target_maximum_length} characters")
        print(f"Processing with {application_config.max_workers} workers...\n")

        success_count = 0
        fail_count = 0

        with ThreadPoolExecutor(max_workers=application_config.max_workers) as executor:
            futures = {executor.submit(process_single_file, fpath): fpath for fpath in media_files}

            with tqdm(total=len(media_files), desc="Processing files", unit="file") as progress_bar:
                for future in as_completed(futures):
                    file_path = futures[future]

                    try:
                        exception = future.exception()
                        if exception:
                            print(f"\n✗ Exception processing {file_path.name}: {exception}\n")
                            fail_count += 1
                        elif future.result():
                            success_count += 1
                        else:
                            fail_count += 1

                    except Exception as error:
                        print(f"\n✗ Unexpected error retrieving result for {file_path.name}: {error}\n")
                        fail_count += 1

                    finally:
                        progress_bar.update(1)
                        progress_bar.set_postfix({
                            'success': success_count,
                            'failed': fail_count
                        })

        separator_line = '=' * 80
        print(f"\n{separator_line}")
        print(f"Processing complete!")
        print(f"Success: {success_count} | Failed: {fail_count} | Total: {len(media_files)}")
        print(f"{separator_line}\n")


if __name__ == '__main__':
    tagger = MediaTagger()
    tagger.process_media()
