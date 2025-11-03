"""Badge database models - re-export from addresses module."""

# Badge model exists in addresses module to maintain Laravel schema compatibility
from src.addresses.models import Badge, address_badge

__all__ = ["Badge", "address_badge"]
