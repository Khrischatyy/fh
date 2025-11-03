"""Photo upload API endpoints."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, UploadFile, File, Form, status, Request
from fastapi.responses import JSONResponse

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.rooms.dependencies import get_room_service
from src.rooms.repository import RoomRepository
from src.photos.service import PhotoService
from src.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/photos", tags=["Photos"])


def get_photo_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> PhotoService:
    """Get photo service instance."""
    from src.rooms.repository import RoomRepository
    room_repo = RoomRepository(db)
    return PhotoService(room_repo)


@router.post(
    "/upload",
    summary="Upload room photos",
    description="Upload one or more photos for a room. Photos are stored in GCS.",
    status_code=status.HTTP_201_CREATED
)
async def upload_photos(
    request: Request,
    service: Annotated[PhotoService, Depends(get_photo_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """
    Upload photos for a room (Laravel-compatible route).

    This endpoint matches Laravel's URL pattern: POST /api/photos/upload

    Form data:
    - photos[]: Multiple photo files (or photos)
    - room_id: Room ID to associate photos with

    Photos are saved to: studios/<studio_slug>/photos/<uuid>.<ext>
    """
    # Parse multipart form data manually to handle photos[0], photos[1], etc.
    form = await request.form()

    # Get room_id
    room_id = form.get("room_id")
    if not room_id:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "room_id is required",
                "code": 400
            }
        )

    try:
        room_id = int(room_id)
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "room_id must be an integer",
                "code": 400
            }
        )

    # Collect all photo files (handle both photos[] and photos[0], photos[1], etc.)
    photos = []
    for key, value in form.items():
        # Check if it's a file field with 'photo' in the name
        # Use hasattr to check if it has file-like methods (handles UploadFile)
        if hasattr(value, 'read') and hasattr(value, 'filename') and 'photo' in key.lower():
            photos.append(value)

    if not photos:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "At least one photo is required",
                "code": 400
            }
        )

    uploaded_photos = []

    for file in photos:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "message": f"Invalid file type: {file.content_type}",
                    "code": 400
                }
            )

        # Upload photo
        photo = await service.upload_room_photo(room_id, file)

        uploaded_photos.append({
            "id": photo.id,
            "path": photo.path,
            "index": photo.index,
            "url": f"/api/photos/image/{photo.path}"  # Proxy URL
        })

    # Return Laravel-compatible format
    return {
        "success": True,
        "data": {
            "room_id": room_id,
            "photos": uploaded_photos,
            "count": len(uploaded_photos)
        },
        "message": f"Successfully uploaded {len(uploaded_photos)} photo(s)",
        "code": 201
    }


@router.get(
    "/image/{photo_path:path}",
    summary="Serve room photo",
    description="Proxy endpoint to serve private photos from GCS.",
)
async def serve_photo(photo_path: str):
    """
    Serve room photo from private GCS bucket.

    This endpoint proxies photos from Google Cloud Storage,
    keeping the files private while serving them through the backend.

    Example: /api/photos/image/studios/my-studio/photos/abc123.jpg
    """
    from fastapi.responses import StreamingResponse
    from fastapi import HTTPException
    from io import BytesIO

    try:
        from src.storage import get_gcs
        gcs = get_gcs()

        # Download the blob
        blob = gcs.bucket.blob(photo_path)

        if not blob.exists():
            raise HTTPException(status_code=404, detail=f"Photo not found: {photo_path}")

        # Download to memory
        image_data = blob.download_as_bytes()

        # Determine content type based on file extension
        if photo_path.endswith(".png"):
            content_type = "image/png"
        elif photo_path.endswith(".jpg") or photo_path.endswith(".jpeg"):
            content_type = "image/jpeg"
        elif photo_path.endswith(".webp"):
            content_type = "image/webp"
        else:
            content_type = "image/jpeg"

        # Return as streaming response
        return StreamingResponse(
            BytesIO(image_data),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache for 1 day
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading photo: {str(e)}")
