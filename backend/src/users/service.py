"""
User service - Business logic for user operations.
Implements Laravel UserService patterns.
"""
from datetime import datetime
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from src.auth.models import User
from src.users.repository import UserRepository


class UserService:
    """Service for user business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserRepository(db)

    async def update_user(
        self,
        user: User,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        username: Optional[str] = None,
        phone: Optional[str] = None,
        date_of_birth: Optional[datetime] = None,
    ) -> User:
        """
        Update user profile fields.
        Only updates provided fields (partial update).

        Args:
            user: User instance to update
            firstname: Optional new firstname
            lastname: Optional new lastname
            username: Optional new username
            phone: Optional new phone
            date_of_birth: Optional new date of birth

        Returns:
            Updated user instance

        Raises:
            HTTPException: If update fails
        """
        try:
            # Update only provided fields
            if firstname is not None:
                user.firstname = firstname
            if lastname is not None:
                user.lastname = lastname
            if username is not None:
                # Check if username already exists
                existing = await self.repository.get_user_by_username(username)
                if existing and existing.id != user.id:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail={
                            "message": "The username has already been taken.",
                            "errors": {"username": ["The username has already been taken."]}
                        }
                    )
                user.username = username
            if phone is not None:
                user.phone = phone
            if date_of_birth is not None:
                user.date_of_birth = date_of_birth

            await self.db.commit()
            await self.db.refresh(user)
            return user
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": f"Failed to update user: {str(e)}",
                    "errors": {}
                }
            )

    async def update_photo(self, user: User, photo: UploadFile) -> str:
        """
        Update user profile photo.
        Converts to JPEG, optimizes, and uploads to GCS.

        Args:
            user: User instance
            photo: Uploaded file

        Returns:
            GCS URL of uploaded photo

        Raises:
            HTTPException: If upload fails
        """
        try:
            from src.storage import gcs_service

            # Generate unique filename
            filename = f"{uuid.uuid4()}.jpg"
            gcs_path = f"profile/photos/{filename}"

            # Read file content
            content = await photo.read()

            # Convert, optimize and upload to GCS
            photo_url = await gcs_service.upload_image(
                content,
                gcs_path,
                convert_to_jpeg=True,
                optimize=True,
                quality=85
            )

            # Update user record
            user.profile_photo = photo_url
            await self.db.commit()
            await self.db.refresh(user)

            return photo_url
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": f"Failed to update photo: {str(e)}",
                    "errors": {}
                }
            )

    async def set_role(self, user: User, role: str) -> str:
        """
        Set user role (one-time operation).
        Users can only set their role once.

        Args:
            user: User instance
            role: Role to set (user or studio_owner)

        Returns:
            The role name

        Raises:
            HTTPException: If user already has role or operation fails
        """
        try:
            # Check if user already has a role (not default "user")
            # In Laravel, this checks if $user->roles->isNotEmpty()
            # We consider a role already set if it's not the default "user" or if it was explicitly set
            if user.role and user.role != "user":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "message": "User already has a role.",
                        "errors": {}
                    }
                )

            # Set the role
            user.role = role
            await self.db.commit()
            await self.db.refresh(user)

            return user.role
        except HTTPException:
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": f"Failed to update role: {str(e)}",
                    "errors": {}
                }
            )
