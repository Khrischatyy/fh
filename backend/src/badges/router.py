"""Badge API endpoints."""

from typing import Annotated
from io import BytesIO

from fastapi import APIRouter, Depends, Query, Path, HTTPException
from fastapi.responses import StreamingResponse

from src.badges.dependencies import get_badge_service
from src.badges.schemas import BadgeResponse, BadgeListResponse, BadgeCreate, BadgeUpdate
from src.badges.service import BadgeService
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.storage import get_gcs

router = APIRouter(prefix="/badges", tags=["badges"])


@router.get("", response_model=BadgeListResponse)
async def get_badges(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: Annotated[BadgeService, Depends(get_badge_service)] = None
):
    """
    Get all available badges.
    Public endpoint - no authentication required.
    """
    return await service.get_all_badges(skip=skip, limit=limit)


@router.get("/{badge_id}", response_model=BadgeResponse)
async def get_badge(
    badge_id: int,
    service: Annotated[BadgeService, Depends(get_badge_service)] = None
):
    """
    Get badge by ID.
    Public endpoint - no authentication required.
    """
    return await service.get_badge(badge_id)


@router.post("", response_model=BadgeResponse)
async def create_badge(
    data: BadgeCreate,
    service: Annotated[BadgeService, Depends(get_badge_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """
    Create new badge.
    Admin only endpoint.
    """
    return await service.create_badge(data)


@router.put("/{badge_id}", response_model=BadgeResponse)
async def update_badge(
    badge_id: int,
    data: BadgeUpdate,
    service: Annotated[BadgeService, Depends(get_badge_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """
    Update existing badge.
    Admin only endpoint.
    """
    return await service.update_badge(badge_id, data)


@router.delete("/{badge_id}", status_code=204)
async def delete_badge(
    badge_id: int,
    service: Annotated[BadgeService, Depends(get_badge_service)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """
    Delete badge.
    Admin only endpoint.
    """
    await service.delete_badge(badge_id)


@router.get("/image/{badge_path:path}", response_class=StreamingResponse)
async def serve_badge_image(
    badge_path: str = Path(..., description="Path to badge image in GCS (e.g., public/badges/mixing.svg)")
):
    """
    Serve badge image from private GCS bucket.

    This endpoint proxies badge images from Google Cloud Storage,
    keeping the files private while serving them through the backend.

    Public endpoint - no authentication required for images.
    """
    try:
        gcs = get_gcs()

        # Download the blob
        blob = gcs.bucket.blob(badge_path)

        if not blob.exists():
            raise HTTPException(status_code=404, detail=f"Badge image not found: {badge_path}")

        # Download to memory
        image_data = blob.download_as_bytes()

        # Determine content type based on file extension
        content_type = "image/svg+xml" if badge_path.endswith(".svg") else "image/png"

        # Return as streaming response
        return StreamingResponse(
            BytesIO(image_data),
            media_type=content_type,
            headers={
                "Cache-Control": "public, max-age=86400",  # Cache for 1 day
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading badge image: {str(e)}")
