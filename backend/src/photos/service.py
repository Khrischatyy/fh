"""Photo upload service."""

import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from src.storage import get_gcs
from src.rooms.models import Room, RoomPhoto
from src.rooms.repository import RoomRepository
from src.exceptions import NotFoundException


class PhotoService:
    """Service for handling photo uploads to GCS."""

    def __init__(self, room_repository: RoomRepository):
        self.room_repository = room_repository
        self.gcs = get_gcs()

    async def upload_room_photo(
        self,
        room_id: int,
        file: UploadFile,
        index: Optional[int] = None
    ) -> RoomPhoto:
        """
        Upload a photo for a room to Google Cloud Storage.

        Saves to: studios/<studio_slug>/photos/<uuid>.<ext>

        Args:
            room_id: Room ID to associate photo with
            file: Uploaded file
            index: Optional display order (auto-assigned if not provided)

        Returns:
            Created RoomPhoto instance

        Raises:
            NotFoundException: If room not found
        """
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        from src.addresses.models import Address

        # Get room with address and company info
        stmt = (
            select(Room)
            .where(Room.id == room_id)
            .options(
                selectinload(Room.address).selectinload(Address.company)
            )
        )
        result = await self.room_repository._session.execute(stmt)
        room = result.scalar_one_or_none()

        if not room:
            raise NotFoundException(f"Room with ID {room_id} not found")

        # Get company slug from room -> address -> company
        company_slug = room.address.company.slug

        # Generate unique filename
        file_ext = Path(file.filename).suffix if file.filename else ".jpg"
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # Build GCS path: studios/<company_slug>/photos/<filename>
        gcs_path = f"studios/{company_slug}/photos/{unique_filename}"

        # Upload to GCS
        file_content = await file.read()

        # Create a temporary file to upload
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name

        try:
            # Upload to GCS
            self.gcs.upload_file(
                source_file_path=tmp_file_path,
                destination_blob_name=gcs_path,
                content_type=file.content_type or "image/jpeg",
                make_public=False  # Keep private, serve via proxy
            )
        finally:
            # Clean up temp file
            Path(tmp_file_path).unlink(missing_ok=True)

        # Determine index for photo ordering
        if index is None:
            existing_photos = await self.room_repository.find_photos_by_room(room_id)
            index = max([p.index for p in existing_photos], default=-1) + 1

        # Create RoomPhoto record
        photo = RoomPhoto(
            room_id=room_id,
            path=gcs_path,  # Store GCS path
            index=index
        )

        return await self.room_repository.create_photo(photo)
