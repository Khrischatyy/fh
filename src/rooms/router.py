"""
Room router - HTTP endpoints for room, price, and photo management.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, status

from src.auth.users import current_active_user
from src.auth.models_fastapi_users import User
from src.rooms.schemas import (
    RoomCreate,
    RoomUpdate,
    RoomResponse,
    RoomWithRelationsResponse,
    RoomPriceCreate,
    RoomPriceUpdate,
    RoomPriceResponse,
    RoomPhotoCreate,
    RoomPhotoUpdate,
    RoomPhotoResponse,
)
from src.rooms.service import RoomService
from src.rooms.dependencies import get_room_service

router = APIRouter(prefix="/rooms", tags=["Rooms"])


# Room Endpoints

@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    data: RoomCreate,
    service: Annotated[RoomService, Depends(get_room_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    """
    Create a new room.

    Matches Laravel route: POST /room/add-room
    """
    room = await service.create_room(data)
    return RoomResponse.model_validate(room)


@router.get("/{room_id}", response_model=RoomWithRelationsResponse, status_code=status.HTTP_200_OK)
async def get_room(
    room_id: int,
    service: Annotated[RoomService, Depends(get_room_service)],
):
    """
    Get room by ID with photos and prices.

    Args:
        room_id: The room ID

    Raises:
        NotFoundException: If room not found
    """
    room = await service.get_room(room_id)
    return RoomWithRelationsResponse.model_validate(room)


@router.patch("/{room_id}", response_model=RoomResponse, status_code=status.HTTP_200_OK)
async def update_room(
    room_id: int,
    data: RoomUpdate,
    service: Annotated[RoomService, Depends(get_room_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    """
    Update room details.

    Matches Laravel route: PUT /room/{room}/update-name
    """
    room = await service.update_room(room_id, data)
    return RoomResponse.model_validate(room)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: int,
    service: Annotated[RoomService, Depends(get_room_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    """
    Delete a room.
    """
    await service.delete_room(room_id)


# Room Price Endpoints

@router.post(
    "/{room_id}/prices",
    response_model=RoomPriceResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_price(
    room_id: int,
    data: RoomPriceCreate,
    service: Annotated[RoomService, Depends(get_room_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    """
    Create a price tier for a room.

    Matches Laravel route: POST /room/{room_id}/prices
    """
    price = await service.create_price(room_id, data)
    return RoomPriceResponse.model_validate(price)


@router.get(
    "/{room_id}/prices",
    response_model=list[RoomPriceResponse],
    status_code=status.HTTP_200_OK
)
async def get_prices(
    room_id: int,
    service: Annotated[RoomService, Depends(get_room_service)],
):
    """
    Get all price tiers for a room.

    Matches Laravel route: GET /room/{room_id}/prices
    """
    prices = await service.get_prices(room_id)
    return [RoomPriceResponse.model_validate(price) for price in prices]


@router.patch("/prices/{price_id}", response_model=RoomPriceResponse, status_code=status.HTTP_200_OK)
async def update_price(
    price_id: int,
    data: RoomPriceUpdate,
    service: Annotated[RoomService, Depends(get_room_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    """
    Update a price tier.

    Note: Laravel route includes this in POST /room/{room_id}/prices with optional ID.
    This is a separate PATCH endpoint for RESTful clarity.
    """
    price = await service.update_price(price_id, data)
    return RoomPriceResponse.model_validate(price)


@router.delete("/prices/{price_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_price(
    price_id: int,
    room_id: int,
    service: Annotated[RoomService, Depends(get_room_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    """
    Delete a price tier.

    Matches Laravel route: DELETE /room/prices (with room_id and room_price_id in body)

    Args:
        price_id: The price ID
        room_id: The room ID (for validation)
    """
    await service.delete_price(price_id, room_id)


# Room Photo Endpoints

@router.post(
    "/{room_id}/photos",
    response_model=RoomPhotoResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_photo(
    room_id: int,
    data: RoomPhotoCreate,
    service: Annotated[RoomService, Depends(get_room_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    """
    Add a photo to a room.

    Matches Laravel route: POST /room/upload
    Note: File upload handling should be added separately.
    """
    photo = await service.create_photo(room_id, data)
    return RoomPhotoResponse.model_validate(photo)


@router.get(
    "/{room_id}/photos",
    response_model=list[RoomPhotoResponse],
    status_code=status.HTTP_200_OK
)
async def get_photos(
    room_id: int,
    service: Annotated[RoomService, Depends(get_room_service)],
):
    """
    Get all photos for a room, ordered by index.
    """
    photos = await service.get_photos(room_id)
    return [RoomPhotoResponse.model_validate(photo) for photo in photos]


@router.patch("/photos/{photo_id}", response_model=RoomPhotoResponse, status_code=status.HTTP_200_OK)
async def update_photo_index(
    photo_id: int,
    data: RoomPhotoUpdate,
    service: Annotated[RoomService, Depends(get_room_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    """
    Update a photo's order index.

    Matches Laravel route: POST /room/update-index
    """
    photo = await service.update_photo_index(photo_id, data.index)
    return RoomPhotoResponse.model_validate(photo)


@router.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(
    photo_id: int,
    service: Annotated[RoomService, Depends(get_room_service)],
    current_user: Annotated[User, Depends(current_active_user)],
):
    """
    Delete a photo.
    """
    await service.delete_photo(photo_id)
