"""
Google Cloud Storage service for file uploads.
Handles image uploads with optimization (JPEG conversion).
"""
from typing import Optional
from io import BytesIO
from PIL import Image
import uuid

from src.config import settings


class GCSService:
    """Google Cloud Storage service for file uploads."""

    def __init__(self):
        """Initialize GCS client."""
        self.bucket_name = settings.gcs_bucket_name
        self.project_id = settings.gcs_project_id
        self._client = None
        self._bucket = None

    def _get_client(self):
        """Lazy load GCS client."""
        if self._client is None:
            from google.cloud import storage
            if settings.gcs_credentials_path:
                self._client = storage.Client.from_service_account_json(
                    settings.gcs_credentials_path,
                    project=self.project_id
                )
            else:
                # Use default credentials (from environment)
                self._client = storage.Client(project=self.project_id)
        return self._client

    def _get_bucket(self):
        """Get GCS bucket."""
        if self._bucket is None:
            client = self._get_client()
            self._bucket = client.bucket(self.bucket_name)
        return self._bucket

    async def upload_image(
        self,
        file_content: bytes,
        destination_path: str,
        convert_to_jpeg: bool = True,
        optimize: bool = True,
        quality: int = 85
    ) -> str:
        """
        Upload image to GCS with optional conversion and optimization.

        Args:
            file_content: Image file bytes
            destination_path: Path in GCS bucket (e.g., 'profile/photos/filename.jpg')
            convert_to_jpeg: Convert image to JPEG format
            optimize: Optimize image file size
            quality: JPEG quality (1-100)

        Returns:
            Public URL of uploaded file

        Raises:
            Exception: If upload fails
        """
        try:
            # Process image if requested
            if convert_to_jpeg or optimize:
                image = Image.open(BytesIO(file_content))

                # Convert to RGB if needed (for JPEG)
                if convert_to_jpeg and image.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                    image = background
                elif convert_to_jpeg and image.mode != 'RGB':
                    image = image.convert('RGB')

                # Save to bytes
                output = BytesIO()
                if convert_to_jpeg:
                    image.save(output, format='JPEG', quality=quality, optimize=optimize)
                else:
                    image.save(output, format=image.format, optimize=optimize)
                file_content = output.getvalue()

            # Upload to GCS
            bucket = self._get_bucket()
            blob = bucket.blob(destination_path)
            blob.upload_from_string(
                file_content,
                content_type='image/jpeg' if convert_to_jpeg else 'image/png'
            )

            # Make blob publicly accessible
            blob.make_public()

            return blob.public_url

        except Exception as e:
            raise Exception(f"Failed to upload to GCS: {str(e)}")

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete file from GCS.

        Args:
            file_path: Path in GCS bucket

        Returns:
            True if deleted successfully
        """
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(file_path)
            blob.delete()
            return True
        except Exception:
            return False


# Global instance
gcs_service = GCSService()
