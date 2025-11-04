"""
Geographic router - HTTP endpoints for countries and cities.
Matches Laravel API routes for backward compatibility.
"""
from typing import Annotated, Any
from fastapi import APIRouter, Depends, status

from src.geographic.schemas import CountryResponse, CityResponse, LaravelResponse
from src.geographic.service import GeographicService
from src.geographic.dependencies import get_geographic_service

router = APIRouter(tags=["Geographic"])


# Countries endpoints
countries_router = APIRouter(prefix="/countries")


@countries_router.get("", response_model=LaravelResponse[list[CountryResponse]], status_code=status.HTTP_200_OK)
async def get_countries(
    service: Annotated[GeographicService, Depends(get_geographic_service)],
):
    """
    Retrieve all countries.

    Returns list of all countries ordered alphabetically by name.
    Laravel compatible: GET /api/countries
    """
    countries = await service.get_all_countries()
    countries_data = [CountryResponse.model_validate(country) for country in countries]

    return LaravelResponse(
        success=True,
        data=countries_data,
        message="Countries received",
        code=200
    )


@countries_router.get(
    "/{country_id}/cities",
    response_model=LaravelResponse[list[CityResponse]],
    status_code=status.HTTP_200_OK,
)
async def get_cities_by_country(
    country_id: int,
    service: Annotated[GeographicService, Depends(get_geographic_service)],
):
    """
    Retrieve all cities for a specific country.

    Args:
        country_id: The country ID

    Returns:
        List of cities in the country, ordered alphabetically

    Laravel compatible: GET /api/countries/{country_id}/cities

    Raises:
        NotFoundException: If country not found
    """
    cities = await service.get_cities_by_country(country_id)
    cities_data = [CityResponse.model_validate(city) for city in cities]

    return LaravelResponse(
        success=True,
        data=cities_data,
        message="Cities received",
        code=200
    )


# City endpoints
city_router = APIRouter(prefix="/city")


@city_router.get(
    "/{city_id}/studios",
    response_model=LaravelResponse[list[Any]],
    status_code=status.HTTP_200_OK,
)
async def get_city_studios(
    city_id: int,
):
    """
    Retrieve all studios (addresses) in a specific city.

    Only returns studios where:
    - Operating hours are configured
    - Payment gateway (Stripe/Square) has payouts enabled

    Args:
        city_id: The city ID

    Returns:
        List of complete studios in the city

    Laravel compatible: GET /api/city/{city_id}/studios

    Raises:
        NotFoundException: If no addresses found
    """
    from src.addresses.repository import AddressRepository
    from src.addresses.service import AddressService
    from src.addresses.utils import build_studio_dict, should_show_in_public_search
    from src.database import AsyncSessionLocal

    # Create database session
    async with AsyncSessionLocal() as session:
        # Create repository and service
        repository = AddressRepository(session)
        address_service = AddressService(repository)

        # Fetch addresses by city
        addresses = await address_service.get_addresses_by_city(city_id)

        if not addresses:
            return LaravelResponse(
                success=False,
                data=[],
                message="No addresses found in the specified city.",
                code=404
            )

        # Cache Stripe account statuses to avoid repeated API calls
        stripe_cache = {}

        # Filter and convert addresses to dict format
        addresses_data = []
        for address in addresses:
            # FILTER: Only include studios that should be shown in public search
            if not should_show_in_public_search(address, stripe_cache):
                continue

            # Build standardized studio dict
            addr_dict = build_studio_dict(
                address,
                include_is_complete=True,
                include_payment_status=True,
                stripe_cache=stripe_cache
            )

            addresses_data.append(addr_dict)

        return LaravelResponse(
            success=True,
            data=addresses_data,
            message="Addresses retrieved successfully.",
            code=200
        )


# Register sub-routers
router.include_router(countries_router)
router.include_router(city_router)
