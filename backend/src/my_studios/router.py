"""
My Studios router - HTTP endpoints for studio owners to manage their studios.
"""
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.my_studios.service import MyStudiosService
from src.my_studios.dependencies import get_my_studios_service
from src.my_studios.schemas import StudioResponse
from src.geographic.schemas import CityResponse


router = APIRouter(prefix="/my-studios", tags=["My Studios"])


class StudioFilterRequest(BaseModel):
    """Request schema for filtering studios."""
    city_id: Optional[int] = None


@router.get(
    "/cities",
    summary="Get cities with user's studios",
    description="Get all unique cities where the authenticated user has studios.",
)
async def get_my_cities(
    service: Annotated[MyStudiosService, Depends(get_my_studios_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get all cities where the current user has studios (Laravel-compatible).

    Returns:
        Laravel-compatible response with list of cities
    """
    cities = await service.get_user_cities(current_user.id)
    cities_data = [CityResponse.model_validate(city).model_dump() for city in cities]

    return {
        "success": True,
        "data": cities_data,
        "message": "Cities retrieved successfully",
        "code": 200
    }


@router.post(
    "/filter",
    summary="Filter user's studios",
    description="Get all studios for the authenticated user, optionally filtered by city.",
)
async def filter_my_studios(
    filter_request: StudioFilterRequest,
    service: Annotated[MyStudiosService, Depends(get_my_studios_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get filtered list of user's studios (Laravel-compatible).

    Args:
        filter_request: Optional filters (city_id)

    Returns:
        Laravel-compatible response with list of addresses/studios
    """
    studios = await service.get_user_studios(
        current_user.id,
        city_id=filter_request.city_id
    )

    # Convert to response format and aggregate photos/prices from rooms
    studios_data = []
    for studio in studios:
        # Convert to dict
        studio_dict = StudioResponse.model_validate(studio).model_dump()

        # Aggregate photos and prices from all rooms
        all_photos = []
        all_prices = []
        for room in studio.rooms:
            all_photos.extend(room.photos)
            all_prices.extend(room.prices)

        # Sort photos by index
        all_photos.sort(key=lambda p: p.index)

        # Add aggregated data
        studio_dict["photos"] = [
            {
                "id": photo.id,
                "room_id": photo.room_id,
                "path": photo.path,
                "index": photo.index,
                "url": f"/api/photos/image/{photo.path}"  # Add proxy URL
            }
            for photo in all_photos
        ]
        studio_dict["prices"] = [
            {
                "id": price.id,
                "room_id": price.room_id,
                "hours": price.hours,
                "total_price": float(price.total_price),
                "price_per_hour": float(price.price_per_hour),
                "is_enabled": price.is_enabled
            }
            for price in all_prices
        ]

        studios_data.append(studio_dict)

    return {
        "success": True,
        "data": studios_data,
        "message": "Studios retrieved successfully",
        "code": 200
    }
