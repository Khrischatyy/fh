"""
SQLAdmin Model Views.
Defines admin views for all database models.
"""
from sqladmin import ModelView
from src.auth.models import User, EngineerRate, PasswordResetToken
from src.addresses.models import (
    Address,
    OperatingMode,
    OperatingHour,
    StudioClosure,
    Equipment,
    EquipmentType,
    Badge,
)
from src.companies.models import Company, AdminCompany
from src.rooms.models import Room, RoomPhoto, RoomPrice
from src.bookings.models import Booking, BookingStatus
from src.geographic.models import Country, City
from src.messages.models import Message
from src.payments.models import Charge, Payout, SquareLocation, SquareToken


class UserAdmin(ModelView, model=User):
    """Admin view for User model."""

    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "Authentication"

    column_list = [
        User.id,
        User.email,
        User.username,
        User.role,
        User.email_verified_at,
        User.created_at,
    ]
    column_searchable_list = [User.email, User.username, User.name]
    column_sortable_list = [User.id, User.email, User.created_at]
    column_default_sort = [(User.id, True)]

    # Allow deletion (cascading is handled by database)
    can_delete = True

    form_excluded_columns = [
        User.created_at,
        User.updated_at,
        User.bookings,
        User.sent_messages,
        User.received_messages,
        User.payouts,
        User.admin_companies,
        User.square_tokens,
        User.favorite_addresses,
        User.engineer_addresses,
        User.engineer_rate,
    ]


class EngineerRateAdmin(ModelView, model=EngineerRate):
    """Admin view for EngineerRate model."""

    name = "Engineer Rate"
    name_plural = "Engineer Rates"
    icon = "fa-solid fa-dollar-sign"
    category = "Authentication"

    column_list = [EngineerRate.id, EngineerRate.user_id, EngineerRate.rate_per_hour]


class PasswordResetTokenAdmin(ModelView, model=PasswordResetToken):
    """Admin view for PasswordResetToken model."""

    name = "Password Reset Token"
    name_plural = "Password Reset Tokens"
    icon = "fa-solid fa-key"
    category = "Authentication"

    column_list = [PasswordResetToken.email, PasswordResetToken.created_at]


class CompanyAdmin(ModelView, model=Company):
    """Admin view for Company model."""

    name = "Company"
    name_plural = "Companies"
    icon = "fa-solid fa-building"
    category = "Studios"

    column_list = [
        Company.id,
        Company.slug,
        Company.name,
        Company.created_at,
    ]
    column_searchable_list = [Company.name, Company.slug]
    column_sortable_list = [Company.id, Company.name, Company.created_at]

    form_excluded_columns = [
        Company.created_at,
        Company.updated_at,
        Company.addresses,
        Company.admin_companies,
    ]


class AdminCompanyAdmin(ModelView, model=AdminCompany):
    """Admin view for AdminCompany model."""

    name = "Admin Company"
    name_plural = "Admin Companies"
    icon = "fa-solid fa-user-tie"
    category = "Studios"

    column_list = [AdminCompany.id, AdminCompany.admin_id, AdminCompany.company_id]


class AddressAdmin(ModelView, model=Address):
    """Admin view for Address model."""

    name = "Studio"
    name_plural = "Studios"
    icon = "fa-solid fa-location-dot"
    category = "Studios"

    column_list = [
        Address.id,
        Address.slug,
        Address.name,
        Address.city_id,
        Address.company_id,
        Address.is_active,
        Address.is_published,
        Address.created_at,
    ]
    column_searchable_list = [Address.name, Address.slug, Address.street]
    column_sortable_list = [Address.id, Address.name, Address.created_at]
    column_filters = [Address.is_active, Address.is_published, Address.city_id]

    form_excluded_columns = [
        Address.created_at,
        Address.updated_at,
        Address.rooms,
        Address.operating_hours,
        Address.studio_closures,
        Address.equipment,
        Address.badges,
        Address.messages,
        Address.engineers,
    ]


class OperatingModeAdmin(ModelView, model=OperatingMode):
    """Admin view for OperatingMode model."""

    name = "Operating Mode"
    name_plural = "Operating Modes"
    icon = "fa-solid fa-clock"
    category = "Studios"

    column_list = [
        OperatingMode.id,
        OperatingMode.mode,
        OperatingMode.label,
    ]


class OperatingHourAdmin(ModelView, model=OperatingHour):
    """Admin view for OperatingHour model."""

    name = "Operating Hour"
    name_plural = "Operating Hours"
    icon = "fa-solid fa-calendar"
    category = "Studios"

    column_list = [
        OperatingHour.id,
        OperatingHour.address_id,
        OperatingHour.mode_id,
        OperatingHour.day_of_week,
        OperatingHour.open_time,
        OperatingHour.close_time,
        OperatingHour.is_closed,
    ]
    column_filters = [OperatingHour.address_id, OperatingHour.day_of_week]

    form_excluded_columns = [OperatingHour.created_at, OperatingHour.updated_at]


class StudioClosureAdmin(ModelView, model=StudioClosure):
    """Admin view for StudioClosure model."""

    name = "Studio Closure"
    name_plural = "Studio Closures"
    icon = "fa-solid fa-door-closed"
    category = "Studios"

    column_list = [
        StudioClosure.id,
        StudioClosure.address_id,
        StudioClosure.start_date,
        StudioClosure.end_date,
        StudioClosure.reason,
    ]
    column_filters = [StudioClosure.address_id]

    form_excluded_columns = [StudioClosure.created_at, StudioClosure.updated_at]


class BadgeAdmin(ModelView, model=Badge):
    """Admin view for Badge model."""

    name = "Badge"
    name_plural = "Badges"
    icon = "fa-solid fa-award"
    category = "Studios"

    column_list = [Badge.id, Badge.name, Badge.description]
    column_searchable_list = [Badge.name, Badge.description]

    form_excluded_columns = [
        Badge.created_at,
        Badge.updated_at,
        Badge.addresses,
    ]


class EquipmentTypeAdmin(ModelView, model=EquipmentType):
    """Admin view for EquipmentType model."""

    name = "Equipment Type"
    name_plural = "Equipment Types"
    icon = "fa-solid fa-list"
    category = "Equipment"

    column_list = [EquipmentType.id, EquipmentType.name]
    column_searchable_list = [EquipmentType.name]

    form_excluded_columns = [
        EquipmentType.created_at,
        EquipmentType.updated_at,
        EquipmentType.equipment,
    ]


class EquipmentAdmin(ModelView, model=Equipment):
    """Admin view for Equipment model."""

    name = "Equipment"
    name_plural = "Equipment"
    icon = "fa-solid fa-toolbox"
    category = "Equipment"

    column_list = [Equipment.id, Equipment.name, Equipment.equipment_type_id]
    column_searchable_list = [Equipment.name]
    column_filters = [Equipment.equipment_type_id]

    form_excluded_columns = [
        Equipment.created_at,
        Equipment.updated_at,
        Equipment.addresses,
    ]


class RoomAdmin(ModelView, model=Room):
    """Admin view for Room model."""

    name = "Room"
    name_plural = "Rooms"
    icon = "fa-solid fa-door-open"
    category = "Rooms"

    column_list = [
        Room.id,
        Room.name,
        Room.address_id,
        Room.created_at,
    ]
    column_searchable_list = [Room.name]
    column_sortable_list = [Room.id, Room.name, Room.created_at]
    column_filters = [Room.address_id]

    form_excluded_columns = [
        Room.created_at,
        Room.updated_at,
        Room.photos,
        Room.prices,
    ]


class RoomPhotoAdmin(ModelView, model=RoomPhoto):
    """Admin view for RoomPhoto model."""

    name = "Room Photo"
    name_plural = "Room Photos"
    icon = "fa-solid fa-image"
    category = "Rooms"

    column_list = [RoomPhoto.id, RoomPhoto.room_id, RoomPhoto.path, RoomPhoto.index]
    column_filters = [RoomPhoto.room_id]


class RoomPriceAdmin(ModelView, model=RoomPrice):
    """Admin view for RoomPrice model."""

    name = "Room Price"
    name_plural = "Room Prices"
    icon = "fa-solid fa-tag"
    category = "Rooms"

    column_list = [
        RoomPrice.id,
        RoomPrice.room_id,
        RoomPrice.hours,
        RoomPrice.total_price,
        RoomPrice.price_per_hour,
        RoomPrice.is_enabled,
    ]
    column_filters = [RoomPrice.room_id]

    form_excluded_columns = [RoomPrice.created_at, RoomPrice.updated_at]


class BookingStatusAdmin(ModelView, model=BookingStatus):
    """Admin view for BookingStatus model."""

    name = "Booking Status"
    name_plural = "Booking Statuses"
    icon = "fa-solid fa-circle-check"
    category = "Bookings"

    column_list = [BookingStatus.id, BookingStatus.name, BookingStatus.description]
    column_searchable_list = [BookingStatus.name]

    form_excluded_columns = [BookingStatus.created_at, BookingStatus.updated_at, BookingStatus.bookings]


class BookingAdmin(ModelView, model=Booking):
    """Admin view for Booking model."""

    name = "Booking"
    name_plural = "Bookings"
    icon = "fa-solid fa-calendar-check"
    category = "Bookings"

    column_list = [
        Booking.id,
        Booking.room_id,
        Booking.user_id,
        Booking.status_id,
        Booking.date,
        Booking.start_time,
        Booking.end_time,
        Booking.created_at,
    ]
    column_filters = [Booking.status_id, Booking.room_id, Booking.user_id]
    column_sortable_list = [Booking.id, Booking.date, Booking.created_at]

    form_excluded_columns = [Booking.created_at, Booking.updated_at]


class CountryAdmin(ModelView, model=Country):
    """Admin view for Country model."""

    name = "Country"
    name_plural = "Countries"
    icon = "fa-solid fa-globe"
    category = "Geographic"

    column_list = [Country.id, Country.name]
    column_searchable_list = [Country.name]
    column_sortable_list = [Country.id, Country.name]

    form_excluded_columns = [Country.cities]


class CityAdmin(ModelView, model=City):
    """Admin view for City model."""

    name = "City"
    name_plural = "Cities"
    icon = "fa-solid fa-city"
    category = "Geographic"

    column_list = [City.id, City.name, City.country_id]
    column_searchable_list = [City.name]
    column_sortable_list = [City.id, City.name]
    column_filters = [City.country_id]

    form_excluded_columns = [City.addresses]


class MessageAdmin(ModelView, model=Message):
    """Admin view for Message model."""

    name = "Message"
    name_plural = "Messages"
    icon = "fa-solid fa-message"
    category = "Communication"

    column_list = [
        Message.id,
        Message.sender_id,
        Message.recipient_id,
        Message.address_id,
        Message.is_read,
        Message.created_at,
    ]
    column_filters = [Message.sender_id, Message.recipient_id, Message.is_read]
    column_sortable_list = [Message.id, Message.created_at]

    form_excluded_columns = [Message.created_at, Message.updated_at, Message.sender, Message.recipient, Message.address]


class ChargeAdmin(ModelView, model=Charge):
    """Admin view for Charge model."""

    name = "Charge"
    name_plural = "Charges"
    icon = "fa-solid fa-credit-card"
    category = "Payments"

    column_list = [
        Charge.id,
        Charge.booking_id,
        Charge.stripe_session_id,
        Charge.square_payment_id,
        Charge.amount,
        Charge.currency,
        Charge.status,
        Charge.created_at,
    ]
    column_filters = [Charge.status, Charge.booking_id]
    column_sortable_list = [Charge.id, Charge.amount, Charge.created_at]

    form_excluded_columns = [Charge.created_at, Charge.updated_at, Charge.booking]


class PayoutAdmin(ModelView, model=Payout):
    """Admin view for Payout model."""

    name = "Payout"
    name_plural = "Payouts"
    icon = "fa-solid fa-money-bill-transfer"
    category = "Payments"

    column_list = [
        Payout.id,
        Payout.user_id,
        Payout.payout_id,
        Payout.amount,
        Payout.currency,
        Payout.status,
        Payout.created_at,
    ]
    column_filters = [Payout.status, Payout.user_id]
    column_sortable_list = [Payout.id, Payout.amount, Payout.created_at]

    # Allow deletion (cascading is handled by database)
    can_delete = True

    form_excluded_columns = [Payout.created_at, Payout.updated_at, Payout.user]


class SquareLocationAdmin(ModelView, model=SquareLocation):
    """Admin view for SquareLocation model."""

    name = "Square Location"
    name_plural = "Square Locations"
    icon = "fa-solid fa-square"
    category = "Payments"

    column_list = [
        SquareLocation.id,
        SquareLocation.user_id,
        SquareLocation.square_location_id,
        SquareLocation.name,
        SquareLocation.is_active,
    ]
    column_filters = [SquareLocation.user_id, SquareLocation.is_active]

    form_excluded_columns = [SquareLocation.created_at, SquareLocation.updated_at]


class SquareTokenAdmin(ModelView, model=SquareToken):
    """Admin view for SquareToken model."""

    name = "Square Token"
    name_plural = "Square Tokens"
    icon = "fa-solid fa-key"
    category = "Payments"

    column_list = [
        SquareToken.id,
        SquareToken.user_id,
        SquareToken.square_location_id,
        SquareToken.expires_at,
    ]
    column_filters = [SquareToken.user_id]

    # Allow deletion (cascading is handled by database)
    can_delete = True

    form_excluded_columns = [
        SquareToken.created_at,
        SquareToken.updated_at,
        SquareToken.access_token,
        SquareToken.refresh_token,
        SquareToken.user,
    ]


# Export all admin views
__all__ = [
    "UserAdmin",
    "EngineerRateAdmin",
    "PasswordResetTokenAdmin",
    "CompanyAdmin",
    "AdminCompanyAdmin",
    "AddressAdmin",
    "OperatingModeAdmin",
    "OperatingHourAdmin",
    "StudioClosureAdmin",
    "BadgeAdmin",
    "EquipmentTypeAdmin",
    "EquipmentAdmin",
    "RoomAdmin",
    "RoomPhotoAdmin",
    "RoomPriceAdmin",
    "BookingStatusAdmin",
    "BookingAdmin",
    "CountryAdmin",
    "CityAdmin",
    "ChargeAdmin",
    "PayoutAdmin",
]
