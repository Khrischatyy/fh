"""
Address/Studio utility functions.
Contains reusable business logic for studio completion and visibility checks.
"""
from typing import Optional, TYPE_CHECKING
import asyncio
import stripe
from redis.asyncio import Redis
from src.config import settings

if TYPE_CHECKING:
    from src.addresses.models import Address
    from src.auth.models import User


# Initialize Stripe
stripe.api_key = settings.stripe_api_key

# Stripe cache constants
STRIPE_CACHE_PREFIX = "stripe_payouts"
STRIPE_CACHE_TTL = 3600  # 1 hour


async def is_studio_complete(address: "Address", redis: Optional[Redis] = None) -> bool:
    """
    Determine if a studio has completed all required setup steps.

    A studio is considered complete when:
    1. Has operating hours configured
    2. Has payment gateway connected (Stripe account with payouts enabled OR Square configured)

    Args:
        address: The Address/studio to check
        redis: Optional Redis client for caching

    Returns:
        True if studio setup is complete, False otherwise
    """
    # Check operating hours
    has_operating_hours = len(address.operating_hours) > 0
    if not has_operating_hours:
        return False

    # Check payment gateway
    has_payment_gateway = await async_has_payment_gateway_connected(address, redis)

    return has_operating_hours and has_payment_gateway


def has_payment_gateway_connected(address: "Address") -> bool:
    """
    Check if studio owner has a payment gateway properly configured (SYNCHRONOUS - DEPRECATED).

    NOTE: This is the old synchronous version kept for backward compatibility.
    Use async_has_payment_gateway_connected() for new code.

    For Stripe: Account must exist AND have payouts enabled
    For Square: Just needs to be configured

    Args:
        address: The Address/studio to check

    Returns:
        True if payment gateway is properly configured
    """
    if not address.company or not address.company.admin_companies:
        return False

    # Get the studio owner (admin)
    studio_owner = None
    for admin_comp in address.company.admin_companies:
        if admin_comp.admin:
            studio_owner = admin_comp.admin
            break

    if not studio_owner:
        return False

    # Check Stripe
    if studio_owner.stripe_account_id:
        # Must verify that Stripe payouts are enabled
        try:
            account = stripe.Account.retrieve(studio_owner.stripe_account_id)
            if account.payouts_enabled:
                return True
        except Exception:
            pass

    # Check Square (if configured, assume it's ready)
    if studio_owner.payment_gateway == 'square':
        return True

    return False


async def async_has_payment_gateway_connected(
    address: "Address", redis: Optional[Redis] = None
) -> bool:
    """
    Check if studio owner has a payment gateway properly configured (ASYNC).

    For Stripe: Account must exist AND have payouts enabled (checked via async API call)
    For Square: Just needs to be configured

    Args:
        address: The Address/studio to check
        redis: Optional Redis client for caching

    Returns:
        True if payment gateway is properly configured
    """
    if not address.company or not address.company.admin_companies:
        return False

    # Get the studio owner (admin)
    studio_owner = get_studio_owner(address)
    if not studio_owner:
        return False

    # Check Stripe
    if studio_owner.stripe_account_id:
        # Must verify that Stripe payouts are enabled (async)
        return await async_check_stripe_payouts_enabled(studio_owner.stripe_account_id, redis)

    # Check Square (if configured, assume it's ready)
    if studio_owner.payment_gateway == 'square':
        return True

    return False


def get_studio_owner(address: "Address") -> Optional["User"]:
    """
    Get the studio owner (admin user) for an address.

    Args:
        address: The Address/studio

    Returns:
        User instance or None if not found
    """
    if not address.company or not address.company.admin_companies:
        return None

    for admin_comp in address.company.admin_companies:
        if admin_comp.admin:
            return admin_comp.admin

    return None


def check_stripe_payouts_enabled(stripe_account_id: str) -> bool:
    """
    Check if a Stripe account has payouts enabled (SYNCHRONOUS - DEPRECATED).

    NOTE: This is the old synchronous version kept for backward compatibility.
    Use async_check_stripe_payouts_enabled() for new code.

    Args:
        stripe_account_id: Stripe Connect account ID

    Returns:
        True if payouts are enabled, False otherwise
    """
    try:
        account = stripe.Account.retrieve(stripe_account_id)
        return account.payouts_enabled
    except Exception:
        return False


async def async_check_stripe_payouts_enabled(
    stripe_account_id: str, redis: Optional[Redis] = None
) -> bool:
    """
    Check if a Stripe account has payouts enabled (ASYNC with caching).

    Uses Stripe SDK's native async method with 3-second timeout.
    Results are cached in Redis for 1 hour to avoid repeated API calls.

    Args:
        stripe_account_id: Stripe Connect account ID
        redis: Optional Redis client for caching

    Returns:
        True if payouts are enabled, False otherwise
    """
    # Check cache first if Redis is available
    if redis:
        cache_key = f"{STRIPE_CACHE_PREFIX}:{stripe_account_id}"
        try:
            cached_value = await redis.get(cache_key)
            if cached_value is not None:
                return cached_value == "1"  # Redis stores as string
        except Exception:
            pass  # Continue without cache if Redis fails

    # Make async request to Stripe API using native SDK method
    try:
        # Use Stripe SDK's native async method with timeout
        async with asyncio.timeout(3):
            account = await stripe.Account.retrieve_async(stripe_account_id)
            payouts_enabled = account.payouts_enabled

            # Cache result if Redis is available
            if redis:
                try:
                    cache_key = f"{STRIPE_CACHE_PREFIX}:{stripe_account_id}"
                    await redis.setex(
                        cache_key,
                        STRIPE_CACHE_TTL,
                        "1" if payouts_enabled else "0",
                    )
                except Exception:
                    pass  # Continue without caching if Redis fails

            return payouts_enabled

    except asyncio.TimeoutError:
        pass  # Return False on timeout
    except stripe.StripeError:
        pass  # Return False on Stripe API error
    except Exception:
        pass  # Catch-all for any other errors

    return False


def _transform_photo_path(path: str) -> str:
    """
    Transform photo path to proxy URL if needed.

    Args:
        path: Original photo path

    Returns:
        Transformed path (proxy URL if not already a full URL)
    """
    if not path:
        return path

    # If already a full URL or proxy URL, return as-is
    if path.startswith('http') or path.startswith('/api/'):
        return path

    # Convert GCS path to proxy URL
    return f"/api/photos/image/{path}"


async def build_studio_dict(
    address: "Address",
    include_is_complete: bool = True,
    include_payment_status: bool = False,
    redis: Optional[Redis] = None
) -> dict:
    """
    Build a standardized dictionary representation of a studio/address (ASYNC).

    This ensures consistent structure across all API endpoints and reduces duplication.

    Args:
        address: The Address model instance
        include_is_complete: Whether to include the is_complete field
        include_payment_status: Whether to include payouts_ready field
        redis: Optional Redis client for caching Stripe account statuses

    Returns:
        Dictionary with standardized studio data
    """
    from src.gcs_utils import get_public_url

    # Build basic studio dict
    studio_dict = {
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
        "badges": [
            {
                "id": b.id,
                "name": b.name,
                "image": get_public_url(b.image) if b.image else None,
                "description": getattr(b, 'description', None),
                "created_at": b.created_at,
                "updated_at": b.updated_at
            }
            for b in address.badges
        ],
        "rooms": [
            {
                "id": r.id,
                "name": r.name,
                "address_id": r.address_id,
                "photos": [
                    {"id": p.id, "path": _transform_photo_path(p.path), "index": p.index}
                    for p in r.photos
                ],
                "prices": [
                    {
                        "id": pr.id,
                        "hours": pr.hours,
                        "total_price": float(pr.total_price),
                        "price_per_hour": float(pr.price_per_hour),
                        "is_enabled": pr.is_enabled
                    }
                    for pr in r.prices if pr.is_enabled
                ],
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
        "equipments": [],  # Frontend expects "equipments" (plural)
    }

    # Add flattened prices and photos (matching Laravel behavior)
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
            for pr in room.prices if pr.is_enabled
        ])
        all_photos.extend([
            {
                "id": p.id,
                "path": _transform_photo_path(p.path),
                "index": p.index
            }
            for p in room.photos
        ])

    studio_dict["prices"] = all_prices
    studio_dict["photos"] = all_photos

    # Add company info
    if address.company:
        studio_dict["company"] = {
            "id": address.company.id,
            "name": address.company.name,
            "slug": address.company.slug,
            "logo": address.company.logo,
        }

        # Add user_id from admin_company
        if address.company.admin_companies:
            for admin_comp in address.company.admin_companies:
                if admin_comp.admin:
                    studio_dict["company"]["user_id"] = admin_comp.admin.id
                    break

    # Add is_complete if requested
    if include_is_complete:
        studio_dict["is_complete"] = await _calculate_is_complete(address, redis)

    # Add payouts_ready if requested (used for filtering)
    if include_payment_status:
        studio_dict["payouts_ready"] = await _calculate_payouts_ready(address, redis)

    return studio_dict


async def _calculate_is_complete(address: "Address", redis: Optional[Redis] = None) -> bool:
    """
    Calculate is_complete field value (ASYNC).

    Studio is complete when:
    - Has operating hours set
    - Has payment gateway with payouts enabled
    """
    has_operating_hours = len(address.operating_hours) > 0
    has_payment = await _calculate_payouts_ready(address, redis)

    return has_operating_hours and has_payment


async def _calculate_payouts_ready(address: "Address", redis: Optional[Redis] = None) -> bool:
    """
    Calculate payouts_ready field value (ASYNC).

    Payouts are ready when:
    - Stripe account has payouts_enabled = True, OR
    - Square payment gateway is configured
    """
    studio_owner = get_studio_owner(address)
    if not studio_owner:
        return False

    # Check Stripe with Redis caching
    if studio_owner.stripe_account_id:
        return await async_check_stripe_payouts_enabled(studio_owner.stripe_account_id, redis)

    # Check Square
    if studio_owner.payment_gateway == 'square':
        return True

    return False


def should_show_in_public_search(address: "Address", stripe_cache: Optional[dict] = None) -> bool:
    """
    Determine if a studio should be shown in public search results.

    Business rules:
    - Studio must be complete (has operating hours + payment gateway)
    - Payment gateway must have payouts enabled

    Args:
        address: The Address/studio to check
        stripe_cache: Optional Stripe cache to avoid repeated API calls

    Returns:
        True if studio should be visible in search, False otherwise
    """
    if stripe_cache is None:
        stripe_cache = {}

    # Must have operating hours
    if len(address.operating_hours) == 0:
        return False

    # Must have payment gateway ready for payouts
    if not _calculate_payouts_ready(address, stripe_cache):
        return False

    return True
