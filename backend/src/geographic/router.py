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

    Only returns studios where the owner has Stripe/Square payouts enabled.

    Args:
        city_id: The city ID

    Returns:
        List of complete addresses in the city with payouts_ready field

    Laravel compatible: GET /api/city/{city_id}/studios

    Raises:
        NotFoundException: If no addresses found
    """
    from src.addresses.repository import AddressRepository
    from src.addresses.service import AddressService
    from src.database import AsyncSessionLocal
    import stripe
    from src.config import settings

    # Initialize Stripe
    stripe.api_key = settings.stripe_api_key

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
        stripe_statuses = {}

        # Convert addresses to dict format for response
        addresses_data = []
        for address in addresses:
            # Check if studio owner has payouts enabled
            payouts_ready = False
            studio_owner = None

            if address.company and address.company.admin_companies:
                for admin_comp in address.company.admin_companies:
                    if admin_comp.admin:
                        studio_owner = admin_comp.admin
                        break

            if studio_owner:
                # Check Stripe payouts
                if studio_owner.stripe_account_id:
                    # Check cache first
                    if studio_owner.stripe_account_id in stripe_statuses:
                        payouts_ready = stripe_statuses[studio_owner.stripe_account_id]
                    else:
                        # Query Stripe API
                        try:
                            account = stripe.Account.retrieve(studio_owner.stripe_account_id)
                            payouts_ready = account.payouts_enabled
                            stripe_statuses[studio_owner.stripe_account_id] = payouts_ready
                        except Exception:
                            payouts_ready = False
                            stripe_statuses[studio_owner.stripe_account_id] = False

                # Check Square (assume ready if configured)
                elif studio_owner.payment_gateway == 'square':
                    payouts_ready = True

            # FILTER: Only include studios where payouts are ready
            if not payouts_ready:
                continue

            # Build address dict with all relationships
            addr_dict = {
                "id": address.id,
                "slug": address.slug,
                "street": address.street,
                "latitude": float(address.latitude) if address.latitude else None,
                "longitude": float(address.longitude) if address.longitude else None,
                "timezone": address.timezone,
                "rating": address.rating,
                "city_id": address.city_id,
                "company_id": address.company_id,
                "available_balance": float(address.available_balance),
                "created_at": address.created_at.isoformat(),
                "updated_at": address.updated_at.isoformat(),
                "badges": [{"id": b.id, "name": b.name} for b in address.badges],
                "rooms": [
                    {
                        "id": r.id,
                        "name": r.name,
                        "photos": [{"id": p.id, "path": p.path, "index": p.index} for p in r.photos],
                        "prices": [{"id": pr.id, "hours": pr.hours, "total_price": float(pr.total_price), "price_per_hour": float(pr.price_per_hour), "is_enabled": pr.is_enabled} for pr in r.prices],
                    }
                    for r in address.rooms
                ],
                "operating_hours": [
                    {
                        "id": oh.id,
                        "day_of_week": oh.day_of_week,
                        "open_time": oh.open_time.isoformat() if oh.open_time else None,
                        "close_time": oh.close_time.isoformat() if oh.close_time else None,
                        "is_closed": oh.is_closed,
                        "mode_id": oh.mode_id,
                    }
                    for oh in address.operating_hours
                ],
                # Frontend expects "equipments" (plural)
                "equipments": [],
                # Add payouts_ready field for frontend
                "payouts_ready": payouts_ready,
            }

            # Add flattened prices and photos (matching Laravel getPricesAttribute and getPhotosAttribute)
            all_prices = []
            all_photos = []
            for room in address.rooms:
                all_prices.extend([
                    {
                        "id": pr.id,
                        "hours": pr.hours,
                        "total_price": float(pr.total_price),
                        "price_per_hour": float(pr.price_per_hour),
                        "is_enabled": pr.is_enabled
                    }
                    for pr in room.prices
                ])
                all_photos.extend([
                    {
                        "id": p.id,
                        "path": p.path,
                        "index": p.index
                    }
                    for p in room.photos
                ])

            addr_dict["prices"] = all_prices
            addr_dict["photos"] = all_photos

            # Calculate is_complete (matching Laravel getIsCompleteAttribute)
            has_operating_hours = len(address.operating_hours) > 0
            has_stripe_gateway = False
            has_square_gateway = False

            if address.company and address.company.admin_companies:
                for admin_comp in address.company.admin_companies:
                    if admin_comp.admin:
                        has_stripe_gateway = admin_comp.admin.stripe_account_id is not None
                        has_square_gateway = admin_comp.admin.payment_gateway == 'square'
                        break

            addr_dict["is_complete"] = has_operating_hours and (has_stripe_gateway or has_square_gateway)

            # Add company info
            if address.company:
                addr_dict["company"] = {
                    "id": address.company.id,
                    "name": address.company.name,
                    "slug": address.company.slug,
                    "logo": address.company.logo,
                    # logo_url intentionally omitted - will be added when S3 integration is ready
                }

                # Add user_id from admin_company
                if address.company.admin_companies:
                    for admin_comp in address.company.admin_companies:
                        if admin_comp.admin:  # Note: relationship is 'admin' not 'user'
                            addr_dict["company"]["user_id"] = admin_comp.admin.id
                            break

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
