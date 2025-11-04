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


@router.get(
    "/",
    summary="Get all user's studios (simple)",
    description="Laravel-compatible GET endpoint to retrieve all user studios with full relationships.",
)
async def get_my_studios_simple(
    service: Annotated[MyStudiosService, Depends(get_my_studios_service)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Get all user's studios with full data (Laravel-compatible).

    Laravel: GET /api/my-studios

    Returns complete studio data with company, badges, rooms, photos, prices, operating hours.
    """
    studios = await service.get_user_studios(current_user.id, city_id=None)
    studios_data = [StudioResponse.model_validate(studio).model_dump() for studio in studios]

    return {
        "success": True,
        "data": studios_data,
        "message": "Studios retrieved successfully.",
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
        Laravel-compatible response with list of addresses/studios with is_complete based on:
        - Operating hours configured
        - Payment gateway (Stripe/Square) with payouts enabled
    """
    from src.addresses.utils import get_studio_owner, check_stripe_payouts_enabled

    studios = await service.get_user_studios(
        current_user.id,
        city_id=filter_request.city_id
    )

    # Stripe cache to avoid repeated API calls
    stripe_cache = {}

    # Convert to response format and aggregate photos/prices from rooms
    studios_data = []
    for studio in studios:
        # Convert to dict
        studio_dict = StudioResponse.model_validate(studio).model_dump()

        # Get studio owner to access payment gateway info
        studio_owner = get_studio_owner(studio)

        # Calculate is_complete based on operating hours + payment gateway
        has_operating_hours = len(studio.operating_hours) > 0
        has_payment_gateway = False
        stripe_account_id = None

        if studio_owner:
            stripe_account_id = studio_owner.stripe_account_id

            # Check Stripe
            if studio_owner.stripe_account_id:
                if studio_owner.stripe_account_id in stripe_cache:
                    has_payment_gateway = stripe_cache[studio_owner.stripe_account_id]
                else:
                    payouts_enabled = check_stripe_payouts_enabled(studio_owner.stripe_account_id)
                    stripe_cache[studio_owner.stripe_account_id] = payouts_enabled
                    has_payment_gateway = payouts_enabled

            # Check Square
            elif studio_owner.payment_gateway == 'square':
                has_payment_gateway = True

        # Set is_complete and stripe_account_id
        studio_dict["is_complete"] = has_operating_hours and has_payment_gateway
        studio_dict["stripe_account_id"] = stripe_account_id

        # Aggregate photos and prices from all rooms
        # Use the Pydantic schema to ensure path transformation is applied
        from src.my_studios.schemas import RoomPhotoResponse, RoomPriceResponse

        all_photos = []
        all_prices = []
        for room in studio.rooms:
            # Convert photos using schema to apply path transformation
            for photo in room.photos:
                photo_response = RoomPhotoResponse.model_validate(photo)
                all_photos.append(photo_response)

            # Convert prices using schema
            for price in room.prices:
                price_response = RoomPriceResponse.model_validate(price)
                all_prices.append(price_response)

        # Sort photos by index
        all_photos.sort(key=lambda p: p.index)

        # Add aggregated data (path is already transformed by schema)
        studio_dict["photos"] = [photo.model_dump() for photo in all_photos]
        studio_dict["prices"] = [
            {
                **price.model_dump(),
                "total_price": float(price.total_price),
                "price_per_hour": float(price.price_per_hour),
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
