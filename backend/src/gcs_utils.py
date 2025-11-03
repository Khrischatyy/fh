"""
Simple GCS utility functions that don't require authentication.
Use this for generating proxied URLs through the backend.
"""

from src.config import settings


def get_public_url(blob_path: str, use_proxy: bool = True) -> str:
    """
    Get URL for a blob in the GCS bucket.

    By default, returns a proxied URL through the backend to keep GCS files private.
    Set use_proxy=False to get direct GCS URLs (files must be public).

    Args:
        blob_path: Path to the file in the bucket (e.g., 'public/badges/mixing.svg')
        use_proxy: If True, return proxied URL through backend. If False, return direct GCS URL.

    Returns:
        URL to access the file
    """
    # If it's already a full URL, return as-is
    if blob_path.startswith("http://") or blob_path.startswith("https://"):
        return blob_path

    if use_proxy:
        # Return proxied URL through backend
        # The frontend will call: http://127.0.0.1/api/badges/image/public/badges/mixing.svg
        return f"/api/badges/image/{blob_path}"
    else:
        # Return direct GCS URL (requires files to be public)
        return f"https://storage.googleapis.com/{settings.gcs_bucket_name}/{blob_path}"
