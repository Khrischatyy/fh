"""
Menu router - Laravel-compatible navigation menu endpoint.
"""
from typing import Annotated, Dict
from fastapi import APIRouter, Depends, status

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.config import settings

router = APIRouter(prefix="/menu", tags=["Menu"])


# Menu items with GCS paths (update these with your actual GCS URLs)
MENU_ITEMS = {
    "history": {
        "name": "History",
        "path": f"https://storage.googleapis.com/{settings.gcs_bucket_name}/public/menu/history.svg"
    },
    "studios_management": {
        "name": "Studios Management",
        "path": f"https://storage.googleapis.com/{settings.gcs_bucket_name}/public/menu/mic.svg"
    },
    "booking_management": {
        "name": "Booking Management",
        "path": f"https://storage.googleapis.com/{settings.gcs_bucket_name}/public/menu/Booking.svg"
    },
    "profile": {
        "name": "Profile",
        "path": f"https://storage.googleapis.com/{settings.gcs_bucket_name}/public/menu/profile.svg"
    }
}


@router.get("", status_code=status.HTTP_200_OK)
async def get_menu(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get role-based navigation menu.

    Laravel compatible: GET /api/menu

    Returns menu items based on user's role:
    - studio_owner: history, studios_management, booking_management, profile
    - user: history, booking_management, profile
    """
    menu_data: Dict[str, Dict[str, str]] = {}

    # Get user role
    user_role = current_user.role

    if user_role == "studio_owner":
        # Studio owners get all 4 menu items
        menu_data = {
            "history": MENU_ITEMS["history"],
            "studios_management": MENU_ITEMS["studios_management"],
            "booking_management": MENU_ITEMS["booking_management"],
            "profile": MENU_ITEMS["profile"]
        }
    elif user_role == "user":
        # Regular users get 3 menu items (no studios management)
        menu_data = {
            "history": MENU_ITEMS["history"],
            "booking_management": MENU_ITEMS["booking_management"],
            "profile": MENU_ITEMS["profile"]
        }
    else:
        # Default (admin or other roles)
        menu_data = MENU_ITEMS

    return {
        "success": True,
        "data": menu_data,
        "message": "Menu items retrieved successfully.",
        "code": 200
    }
