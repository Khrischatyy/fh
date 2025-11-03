"""Google Cloud Storage utility."""

import os
from pathlib import Path
from typing import Optional

from google.cloud import storage
from google.oauth2 import service_account

from src.config import settings


class GoogleCloudStorage:
    """Google Cloud Storage client wrapper."""

    def __init__(self):
        """Initialize GCS client with service account credentials."""
        # Try multiple locations for the credentials file
        possible_paths = [
            Path(__file__).parent.parent / "safeturf-main-c4c022f13d42.json",  # backend/
            Path("/app/safeturf-main-c4c022f13d42.json"),  # Docker container root
            Path.cwd() / "safeturf-main-c4c022f13d42.json",  # Current working directory
        ]

        # Check for environment variable override
        env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if env_path:
            possible_paths.insert(0, Path(env_path))

        credentials_path = None
        for path in possible_paths:
            if path.exists():
                credentials_path = path
                break

        if not credentials_path:
            raise FileNotFoundError(
                f"Google Cloud credentials file not found. Tried:\n" +
                "\n".join(f"  - {p}" for p in possible_paths) +
                "\nPlease add the service account JSON file or set GOOGLE_APPLICATION_CREDENTIALS env var."
            )

        self.credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path)
        )
        self.client = storage.Client(credentials=self.credentials)
        self.bucket_name = settings.gcs_bucket_name
        self.bucket = self.client.bucket(self.bucket_name)

    def get_public_url(self, blob_path: str) -> str:
        """
        Get public URL for a blob in the bucket.

        Args:
            blob_path: Path to the file in the bucket (e.g., 'public/badges/mixing.svg')

        Returns:
            Public URL to access the file
        """
        # If it's already a full URL, return as-is
        if blob_path.startswith("http://") or blob_path.startswith("https://"):
            return blob_path

        return f"https://storage.googleapis.com/{self.bucket_name}/{blob_path}"

    def upload_file(
        self,
        source_file_path: str,
        destination_blob_name: str,
        content_type: Optional[str] = None,
        make_public: bool = True
    ) -> str:
        """
        Upload a file to Google Cloud Storage.

        Args:
            source_file_path: Local file path to upload
            destination_blob_name: Destination path in bucket
            content_type: MIME type of the file
            make_public: Whether to make the file publicly accessible

        Returns:
            Public URL of the uploaded file
        """
        blob = self.bucket.blob(destination_blob_name)

        if content_type:
            blob.content_type = content_type

        blob.upload_from_filename(source_file_path)

        if make_public:
            blob.make_public()

        return blob.public_url

    def make_blob_public(self, blob_path: str) -> str:
        """
        Make an existing blob publicly accessible.

        Args:
            blob_path: Path to the file in the bucket

        Returns:
            Public URL of the file
        """
        blob = self.bucket.blob(blob_path)
        blob.make_public()
        return blob.public_url

    def list_blobs(self, prefix: Optional[str] = None) -> list[str]:
        """
        List all blobs in the bucket with optional prefix filter.

        Args:
            prefix: Filter blobs by prefix (e.g., 'public/badges/')

        Returns:
            List of blob names
        """
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
        return [blob.name for blob in blobs]


# Singleton instance
_gcs_instance: Optional[GoogleCloudStorage] = None


def get_gcs() -> GoogleCloudStorage:
    """Get or create GoogleCloudStorage singleton instance."""
    global _gcs_instance
    if _gcs_instance is None:
        _gcs_instance = GoogleCloudStorage()
    return _gcs_instance