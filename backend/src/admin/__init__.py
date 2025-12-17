"""
Admin Panel Module.
Provides SQLAdmin interface with email-based authentication.
"""
from sqladmin import Admin

from src.admin.auth import SuperuserAuthBackend
from src.admin.views import (
    UserAdmin,
    EngineerRateAdmin,
    PasswordResetTokenAdmin,
    CompanyAdmin,
    AdminCompanyAdmin,
    AddressAdmin,
    OperatingModeAdmin,
    OperatingHourAdmin,
    BadgeAdmin,
    EquipmentTypeAdmin,
    EquipmentAdmin,
    RoomAdmin,
    RoomPhotoAdmin,
    RoomPriceAdmin,
    BookingStatusAdmin,
    BookingAdmin,
    CountryAdmin,
    CityAdmin,
    MessageAdmin,
    DeviceAdmin,
    DeviceLogAdmin,
)
from src.config import settings


def setup_admin(app, engine):
    """
    Setup SQLAdmin with all model views.

    Args:
        app: FastAPI application instance
        engine: SQLAlchemy sync engine

    Returns:
        Admin: Configured SQLAdmin instance
    """
    # Create authentication backend
    authentication_backend = SuperuserAuthBackend(secret_key=settings.admin_secret_key)

    # Create admin with authentication
    admin = Admin(
        app,
        engine,
        title="Funny How Admin",
        authentication_backend=authentication_backend,
    )

    # Register all views
    admin.add_view(UserAdmin)
    admin.add_view(EngineerRateAdmin)
    admin.add_view(PasswordResetTokenAdmin)
    admin.add_view(CompanyAdmin)
    admin.add_view(AdminCompanyAdmin)
    admin.add_view(AddressAdmin)
    admin.add_view(OperatingModeAdmin)
    admin.add_view(OperatingHourAdmin)
    admin.add_view(BadgeAdmin)
    admin.add_view(EquipmentTypeAdmin)
    admin.add_view(EquipmentAdmin)
    admin.add_view(RoomAdmin)
    admin.add_view(RoomPhotoAdmin)
    admin.add_view(RoomPriceAdmin)
    admin.add_view(BookingStatusAdmin)
    admin.add_view(BookingAdmin)
    admin.add_view(CountryAdmin)
    admin.add_view(CityAdmin)
    admin.add_view(MessageAdmin)
    admin.add_view(DeviceAdmin)
    admin.add_view(DeviceLogAdmin)

    return admin


__all__ = ["setup_admin", "SuperuserAuthBackend"]
