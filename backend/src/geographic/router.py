"""
Geographic router - HTTP endpoints for countries and cities.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, status

from src.geographic.schemas import CountryResponse, CityResponse
from src.geographic.service import GeographicService
from src.geographic.dependencies import get_geographic_service

router = APIRouter(prefix="/geographic", tags=["Geographic"])


@router.get("/countries", response_model=list[CountryResponse], status_code=status.HTTP_200_OK)
async def get_countries(
    service: Annotated[GeographicService, Depends(get_geographic_service)],
):
    """
    Retrieve all countries.

    Returns list of all countries ordered alphabetically by name.
    """
    countries = await service.get_all_countries()
    return [CountryResponse.model_validate(country) for country in countries]


@router.get(
    "/countries/{country_id}",
    response_model=CountryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_country(
    country_id: int,
    service: Annotated[GeographicService, Depends(get_geographic_service)],
):
    """
    Get a specific country by ID.

    Args:
        country_id: The country ID

    Raises:
        NotFoundException: If country not found
    """
    country = await service.get_country(country_id)
    return CountryResponse.model_validate(country)


@router.get(
    "/countries/{country_id}/cities",
    response_model=list[CityResponse],
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

    Raises:
        NotFoundException: If country not found
    """
    cities = await service.get_cities_by_country(country_id)
    return [CityResponse.model_validate(city) for city in cities]


@router.get("/cities/{city_id}", response_model=CityResponse, status_code=status.HTTP_200_OK)
async def get_city(
    city_id: int,
    service: Annotated[GeographicService, Depends(get_geographic_service)],
):
    """
    Get a specific city by ID.

    Args:
        city_id: The city ID

    Raises:
        NotFoundException: If city not found
    """
    city = await service.get_city(city_id)
    return CityResponse.model_validate(city)
