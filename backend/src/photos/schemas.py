"""
Photo schemas for request/response validation.
"""
from pydantic import BaseModel, Field


class PhotoUploadResponse(BaseModel):
    """Response for photo upload."""
    id: int
    room_id: int
    path: str
    index: int


class UpdatePhotoIndexRequest(BaseModel):
    """Request for updating photo index."""
    room_photo_id: int = Field(..., gt=0, description="Photo ID")
    index: int = Field(..., ge=0, description="New index position")
