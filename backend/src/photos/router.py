"""
Photos router - Laravel-compatible endpoints for photo upload and management.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, status, File, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from starlette.datastructures import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.database import get_db
from src.photos.service import PhotoService
from src.photos.schemas import PhotoUploadResponse, UpdatePhotoIndexRequest
from src.config import settings

router = APIRouter(prefix="/photos", tags=["Photos"])


@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_photos(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Upload multiple photos for a room.

    Laravel compatible: POST /api/photos/upload

    Args:
        room_id: Room ID (from form data)
        photos: Array of image files (jpeg, png, jpg, gif, svg, heic, heif - max 5MB each)
                Can be sent as 'photos' array or Laravel-style 'photos[0]', 'photos[1]', etc.

    Returns:
        Array of uploaded photo objects with path and index
    """
    # Parse multipart form data manually to support Laravel array notation
    form = await request.form()

    # Extract room_id
    room_id = form.get("room_id")
    if not room_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Room ID is required.",
                "errors": {"room_id": ["The room id field is required."]}
            }
        )

    try:
        room_id = int(room_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Room ID must be an integer.",
                "errors": {"room_id": ["The room id must be an integer."]}
            }
        )

    # Extract photos - support both 'photos' and 'photos[0]', 'photos[1]', etc.
    photos = []

    # Check for standard 'photos' field
    if "photos" in form:
        photos_field = form.getlist("photos")
        photos.extend([p for p in photos_field if isinstance(p, UploadFile)])

    # Check for Laravel-style array notation: photos[0], photos[1], etc.
    for key in form.keys():
        if key.startswith("photos[") and key.endswith("]"):
            file = form.get(key)
            if isinstance(file, UploadFile):
                photos.append(file)

    # Validate at least one photo
    if not photos:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "At least one photo is required.",
                "errors": {"photos": ["At least one photo is required."]}
            }
        )

    # Validate each photo
    allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/gif", "image/svg+xml", "image/heic", "image/heif"]
    max_size = 5120 * 1024  # 5MB in bytes

    for idx, photo in enumerate(photos):
        if photo.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": f"Photo {idx + 1} must be a file of type: jpeg, png, jpg, gif, svg, heic, heif.",
                    "errors": {f"photos.{idx}": [f"The photo must be a file of type: jpeg, png, jpg, gif, svg, heic, heif."]}
                }
            )

        # Check file size
        content = await photo.read()
        await photo.seek(0)  # Reset pointer
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": f"Photo {idx + 1} must not be greater than 5120 kilobytes.",
                    "errors": {f"photos.{idx}": ["The photo must not be greater than 5120 kilobytes."]}
                }
            )

    try:
        service = PhotoService(db)
        uploaded_photos = await service.upload_photos(room_id, photos)

        # Format response
        photos_data = [
            {
                "id": photo.id,
                "room_id": photo.room_id,
                "path": photo.path,
                "index": photo.index,
                "created_at": photo.created_at.isoformat() if hasattr(photo, 'created_at') and photo.created_at else None,
                "updated_at": photo.updated_at.isoformat() if hasattr(photo, 'updated_at') and photo.updated_at else None,
            }
            for photo in uploaded_photos
        ]

        return {
            "success": True,
            "data": photos_data,
            "message": "Photos uploaded successfully.",
            "code": 200
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Failed to upload photos: {str(e)}",
                "errors": {}
            }
        )


@router.post("/update-index", status_code=status.HTTP_200_OK)
async def update_photo_index(
    request: UpdatePhotoIndexRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Update photo order index with swap logic.

    Laravel compatible: POST /api/photos/update-index

    Args:
        request: Photo ID and new index

    Returns:
        Updated photo object

    Note:
        If another photo has the target index, they will be swapped automatically.
    """
    try:
        service = PhotoService(db)
        updated_photo = await service.update_photo_index(
            request.room_photo_id,
            request.index
        )

        # Format response
        photo_data = {
            "id": updated_photo.id,
            "room_id": updated_photo.room_id,
            "path": updated_photo.path,
            "index": updated_photo.index,
            "created_at": updated_photo.created_at.isoformat() if hasattr(updated_photo, 'created_at') and updated_photo.created_at else None,
            "updated_at": updated_photo.updated_at.isoformat() if hasattr(updated_photo, 'updated_at') and updated_photo.updated_at else None,
        }

        return {
            "success": True,
            "data": photo_data,
            "message": "Photo index updated successfully.",
            "code": 200
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Failed to update photo index: {str(e)}",
                "errors": {}
            }
        )


@router.get("/image/{path:path}")
async def get_photo_image(path: str):
    """
    Proxy endpoint to serve images from GCS.

    This endpoint fetches the image from GCS using service account credentials
    and returns it to the client (since the bucket is not publicly readable).

    Args:
        path: Path to the image in GCS (e.g., 'studio/photos/abc123.jpg')

    Returns:
        Image file
    """
    from google.cloud import storage
    from fastapi.responses import StreamingResponse
    import os
    import io

    try:
        # Initialize GCS client with credentials
        credentials_path = settings.gcs_credentials_path
        if credentials_path and os.path.exists(credentials_path):
            client = storage.Client.from_service_account_json(
                credentials_path,
                project=settings.gcs_project_id
            )
        else:
            client = storage.Client(project=settings.gcs_project_id)

        # Get the blob
        bucket = client.bucket(settings.gcs_bucket_name)
        blob = bucket.blob(path)

        # Download to memory
        image_data = blob.download_as_bytes()

        # Determine content type
        content_type = "image/jpeg"
        if path.endswith(".png"):
            content_type = "image/png"
        elif path.endswith(".gif"):
            content_type = "image/gif"
        elif path.endswith(".webp"):
            content_type = "image/webp"

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(image_data),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache for 1 day
                "Content-Disposition": f'inline; filename="{path.split("/")[-1]}"'
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"Image not found: {str(e)}",
                "errors": {}
            }
        )
