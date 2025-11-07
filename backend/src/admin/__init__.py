"""
Admin Panel Module.
Provides SQLAdmin interface with basic HTTP authentication.
"""
from sqladmin import Admin
from src.admin.auth import BasicAuthBackend
from src.admin.views import (
    UserAdmin,
    EngineerRateAdmin,
    PasswordResetTokenAdmin,
    CompanyAdmin,
    AdminCompanyAdmin,
    AddressAdmin,
    OperatingModeAdmin,
    OperatingHourAdmin,
    StudioClosureAdmin,
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
    ChargeAdmin,
    PayoutAdmin,
)


def setup_admin(app, engine):
    """
    Setup SQLAdmin with all model views.

    Args:
        app: FastAPI application instance
        engine: SQLAlchemy async engine

    Returns:
        Admin: Configured SQLAdmin instance
    """
    from src.config import settings

    # Create authentication backend
    authentication_backend = BasicAuthBackend(secret_key=settings.admin_secret_key)

    # Initialize admin
    admin = Admin(
        app,
        engine,
        title="Funny How Admin",
        authentication_backend=authentication_backend,
    )

    # Register Authentication views
    admin.add_view(UserAdmin)
    admin.add_view(EngineerRateAdmin)
    admin.add_view(PasswordResetTokenAdmin)

    # Register Studio views
    admin.add_view(CompanyAdmin)
    admin.add_view(AdminCompanyAdmin)
    admin.add_view(AddressAdmin)
    admin.add_view(OperatingModeAdmin)
    admin.add_view(OperatingHourAdmin)
    admin.add_view(StudioClosureAdmin)
    admin.add_view(BadgeAdmin)

    # Register Equipment views
    admin.add_view(EquipmentTypeAdmin)
    admin.add_view(EquipmentAdmin)

    # Register Room views
    admin.add_view(RoomAdmin)
    admin.add_view(RoomPhotoAdmin)
    admin.add_view(RoomPriceAdmin)

    # Register Booking views
    admin.add_view(BookingStatusAdmin)
    admin.add_view(BookingAdmin)

    # Register Geographic views
    admin.add_view(CountryAdmin)
    admin.add_view(CityAdmin)

    # Register Payment views
    admin.add_view(ChargeAdmin)
    admin.add_view(PayoutAdmin)

    return admin


__all__ = ["setup_admin", "BasicAuthBackend"]
