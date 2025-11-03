"""
Photo service - Business logic for photo upload and management.
Implements Laravel PhotoService patterns.
"""
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from src.rooms.models import Room, RoomPhoto
from src.exceptions import NotFoundException


class PhotoService:
    """Service for photo operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_photos(self, room_id: int, photos: list[UploadFile]) -> list[RoomPhoto]:
        """
        Upload multiple photos for a room.
        Converts to JPEG, optimizes, uploads to GCS, and creates database records.

        Args:
            room_id: Room ID
            photos: List of uploaded files

        Returns:
            List of created RoomPhoto objects

        Raises:
            HTTPException: If room not found or upload fails
        """
        from src.storage import gcs_service

        # Verify room exists
        stmt = select(Room).where(Room.id == room_id)
        result = await self.db.execute(stmt)
        room = result.scalar_one_or_none()

        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "message": f"Room with ID {room_id} not found.",
                    "errors": {}
                }
            )

        # Get current max index
        stmt = select(RoomPhoto).where(RoomPhoto.room_id == room_id)
        result = await self.db.execute(stmt)
        existing_photos = result.scalars().all()
        max_index = max([p.index for p in existing_photos], default=-1)

        uploaded_photos = []

        for photo_file in photos:
            try:
                # Generate unique filename
                filename = f"{uuid.uuid4().hex}.jpg"
                gcs_path = f"studio/photos/{filename}"

                # Read file content
                content = await photo_file.read()

                # Upload to GCS with conversion and optimization
                photo_url = await gcs_service.upload_image(
                    content,
                    gcs_path,
                    convert_to_jpeg=True,
                    optimize=True,
                    quality=85
                )

                # Increment index
                max_index += 1

                # Create database record
                room_photo = RoomPhoto(
                    room_id=room_id,
                    path=photo_url,
                    index=max_index
                )
                self.db.add(room_photo)
                uploaded_photos.append(room_photo)

            except Exception as e:
                await self.db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "message": f"Failed to upload photo: {str(e)}",
                        "errors": {}
                    }
                )

        # Commit all photos
        await self.db.commit()

        # Refresh to get IDs and timestamps
        for photo in uploaded_photos:
            await self.db.refresh(photo)

        return uploaded_photos

    async def update_photo_index(self, photo_id: int, new_index: int) -> RoomPhoto:
        """
        Update photo index with swap logic to maintain unique constraint.

        If another photo has the target index, swaps them using temporary index.

        Args:
            photo_id: Photo ID to update
            new_index: New index value

        Returns:
            Updated photo

        Raises:
            HTTPException: If photo not found or update fails
        """
        try:
            # Find the photo to update
            stmt = select(RoomPhoto).where(RoomPhoto.id == photo_id)
            result = await self.db.execute(stmt)
            photo = result.scalar_one_or_none()

            if not photo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "message": f"Photo with ID {photo_id} not found.",
                        "errors": {}
                    }
                )

            old_index = photo.index

            # If index is the same, no change needed
            if old_index == new_index:
                return photo

            # Find if another photo has the target index in the same room
            stmt = select(RoomPhoto).where(
                RoomPhoto.room_id == photo.room_id,
                RoomPhoto.index == new_index
            )
            result = await self.db.execute(stmt)
            conflicting_photo = result.scalar_one_or_none()

            if conflicting_photo:
                # Swap logic: use temporary index
                temp_index = new_index + 1000

                # Move conflicting photo to temp
                conflicting_photo.index = temp_index
                await self.db.flush()

                # Move current photo to new index
                photo.index = new_index
                await self.db.flush()

                # Move conflicting photo to old index
                conflicting_photo.index = old_index
                await self.db.flush()
            else:
                # No conflict, just update
                photo.index = new_index

            await self.db.commit()
            await self.db.refresh(photo)

            return photo

        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": f"Failed to update photo index: {str(e)}",
                    "errors": {}
                }
            )
