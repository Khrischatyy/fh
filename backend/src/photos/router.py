"""
Photos router - Laravel-compatible endpoints for photo upload and management.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.database import get_db
from src.photos.service import PhotoService
from src.photos.schemas import PhotoUploadResponse, UpdatePhotoIndexRequest

router = APIRouter(prefix="/photos", tags=["Photos"])


@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_photos(
    room_id: Annotated[int, Form(...)],
    photos: Annotated[list[UploadFile], File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Upload multiple photos for a room.

    Laravel compatible: POST /api/photos/upload

    Args:
        room_id: Room ID
        photos: Array of image files (jpeg, png, jpg, gif, svg, heic, heif - max 5MB each)

    Returns:
        Array of uploaded photo objects with path and index
    """
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
