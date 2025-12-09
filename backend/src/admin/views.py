"""
SQLAdmin Model Views.
Defines admin views for all database models with proper FK displays.
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
from src.payments.models import Charge, Payout, SquareLocation, SquareToken
from src.devices.models import Device, DeviceLog
from src.messages.models import Message


# ============================================================================
# AUTHENTICATION
# ============================================================================

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
        User.firstname,
        User.lastname,
        User.role,
        User.is_superuser,
        User.email_verified_at,
        User.created_at,
    ]

    column_sortable_list = [User.id, User.email, User.created_at]
    column_searchable_list = [User.email, User.username, User.firstname, User.lastname]
    column_default_sort = [(User.id, True)]


class EngineerRateAdmin(ModelView, model=EngineerRate):
    """Admin view for EngineerRate model."""
    name = "Engineer Rate"
    name_plural = "Engineer Rates"
    icon = "fa-solid fa-dollar-sign"
    category = "Authentication"

    column_list = [
        EngineerRate.id,
        EngineerRate.user,
        EngineerRate.rate_per_hour,
    ]


class PasswordResetTokenAdmin(ModelView, model=PasswordResetToken):
    """Admin view for PasswordResetToken model."""
    name = "Password Reset Token"
    name_plural = "Password Reset Tokens"
    icon = "fa-solid fa-key"
    category = "Authentication"

    column_list = [
        PasswordResetToken.email,
        PasswordResetToken.created_at,
    ]


# ============================================================================
# STUDIOS / COMPANIES
# ============================================================================

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

    column_sortable_list = [Company.id, Company.name, Company.created_at]
    column_searchable_list = [Company.name, Company.slug]
    column_default_sort = [(Company.id, True)]


class AdminCompanyAdmin(ModelView, model=AdminCompany):
    """Admin view for AdminCompany model."""
    name = "Admin Company"
    name_plural = "Admin Companies"
    icon = "fa-solid fa-user-tie"
    category = "Studios"

    column_list = [
        AdminCompany.id,
        AdminCompany.admin,
        AdminCompany.company,
    ]


class AddressAdmin(ModelView, model=Address):
    """Admin view for Address model."""
    name = "Address"
    name_plural = "Addresses"
    icon = "fa-solid fa-location-dot"
    category = "Studios"

    column_list = [
        Address.id,
        Address.slug,
        Address.name,
        Address.street,
        Address.city,
        Address.company,
        Address.is_active,
        Address.is_published,
        Address.created_at,
    ]

    column_sortable_list = [Address.id, Address.name, Address.created_at]
    column_searchable_list = [Address.name, Address.slug, Address.street]
    column_default_sort = [(Address.id, True)]


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
        OperatingHour.address,
        OperatingHour.mode_id,
        OperatingHour.day_of_week,
        OperatingHour.open_time,
        OperatingHour.close_time,
        OperatingHour.is_closed,
    ]


class BadgeAdmin(ModelView, model=Badge):
    """Admin view for Badge model."""
    name = "Badge"
    name_plural = "Badges"
    icon = "fa-solid fa-award"
    category = "Studios"

    column_list = [
        Badge.id,
        Badge.name,
        Badge.description,
        Badge.image,
    ]

    column_searchable_list = [Badge.name, Badge.description]


# ============================================================================
# EQUIPMENT
# ============================================================================

class EquipmentTypeAdmin(ModelView, model=EquipmentType):
    """Admin view for EquipmentType model."""
    name = "Equipment Type"
    name_plural = "Equipment Types"
    icon = "fa-solid fa-list"
    category = "Equipment"

    column_list = [
        EquipmentType.id,
        EquipmentType.name,
    ]

    column_searchable_list = [EquipmentType.name]


class EquipmentAdmin(ModelView, model=Equipment):
    """Admin view for Equipment model."""
    name = "Equipment"
    name_plural = "Equipment"
    icon = "fa-solid fa-toolbox"
    category = "Equipment"

    column_list = [
        Equipment.id,
        Equipment.name,
        Equipment.equipment_type,
    ]

    column_searchable_list = [Equipment.name]


# ============================================================================
# ROOMS
# ============================================================================

class RoomAdmin(ModelView, model=Room):
    """Admin view for Room model."""
    name = "Room"
    name_plural = "Rooms"
    icon = "fa-solid fa-door-open"
    category = "Rooms"

    column_list = [
        Room.id,
        Room.name,
        Room.address,
        Room.created_at,
    ]

    column_sortable_list = [Room.id, Room.name, Room.created_at]
    column_searchable_list = [Room.name]
    column_default_sort = [(Room.id, True)]


class RoomPhotoAdmin(ModelView, model=RoomPhoto):
    """Admin view for RoomPhoto model."""
    name = "Room Photo"
    name_plural = "Room Photos"
    icon = "fa-solid fa-image"
    category = "Rooms"

    column_list = [
        RoomPhoto.id,
        RoomPhoto.room,
        RoomPhoto.path,
        RoomPhoto.index,
    ]


class RoomPriceAdmin(ModelView, model=RoomPrice):
    """Admin view for RoomPrice model."""
    name = "Room Price"
    name_plural = "Room Prices"
    icon = "fa-solid fa-tag"
    category = "Rooms"

    column_list = [
        RoomPrice.id,
        RoomPrice.room,
        RoomPrice.hours,
        RoomPrice.total_price,
        RoomPrice.price_per_hour,
        RoomPrice.is_enabled,
    ]


# ============================================================================
# BOOKINGS
# ============================================================================

class BookingStatusAdmin(ModelView, model=BookingStatus):
    """Admin view for BookingStatus model."""
    name = "Booking Status"
    name_plural = "Booking Statuses"
    icon = "fa-solid fa-circle-check"
    category = "Bookings"

    column_list = [
        BookingStatus.id,
        BookingStatus.name,
    ]

    column_searchable_list = [BookingStatus.name]


class BookingAdmin(ModelView, model=Booking):
    """Admin view for Booking model."""
    name = "Booking"
    name_plural = "Bookings"
    icon = "fa-solid fa-calendar-check"
    category = "Bookings"

    column_list = [
        Booking.id,
        Booking.room,
        Booking.user,
        Booking.status,
        Booking.date,
        Booking.start_time,
        Booking.end_time,
        Booking.device,
        Booking.created_at,
    ]

    column_sortable_list = [Booking.id, Booking.date, Booking.created_at]
    column_default_sort = [(Booking.id, True)]


# ============================================================================
# GEOGRAPHIC
# ============================================================================

class CountryAdmin(ModelView, model=Country):
    """Admin view for Country model."""
    name = "Country"
    name_plural = "Countries"
    icon = "fa-solid fa-globe"
    category = "Geographic"

    column_list = [
        Country.id,
        Country.name,
    ]

    column_sortable_list = [Country.id, Country.name]
    column_searchable_list = [Country.name]
    column_default_sort = [(Country.id, True)]


class CityAdmin(ModelView, model=City):
    """Admin view for City model."""
    name = "City"
    name_plural = "Cities"
    icon = "fa-solid fa-city"
    category = "Geographic"

    column_list = [
        City.id,
        City.name,
        City.country,
    ]

    column_sortable_list = [City.id, City.name]
    column_searchable_list = [City.name]
    column_default_sort = [(City.id, True)]


# ============================================================================
# COMMUNICATION
# ============================================================================

class MessageAdmin(ModelView, model=Message):
    """Admin view for Message model."""
    name = "Message"
    name_plural = "Messages"
    icon = "fa-solid fa-message"
    category = "Communication"

    column_list = [
        Message.id,
        Message.sender,
        Message.recipient,
        Message.address,
        Message.content,
        Message.is_read,
        Message.created_at,
    ]

    column_sortable_list = [Message.id, Message.created_at]
    column_default_sort = [(Message.id, True)]


# ============================================================================
# DEVICES
# ============================================================================

class DeviceAdmin(ModelView, model=Device):
    """Admin view for Device model."""
    name = "Device"
    name_plural = "Devices"
    icon = "fa-solid fa-laptop"
    category = "Devices"

    column_list = [
        Device.id,
        Device.name,
        Device.mac_address,
        Device.device_uuid,
        Device.user,
        Device.is_blocked,
        Device.is_active,
        Device.last_heartbeat,
        Device.created_at,
    ]

    column_sortable_list = [Device.id, Device.name, Device.created_at, Device.last_heartbeat]
    column_searchable_list = [Device.name, Device.mac_address, Device.device_uuid]
    column_default_sort = [(Device.id, True)]


class DeviceLogAdmin(ModelView, model=DeviceLog):
    """Admin view for DeviceLog model."""
    name = "Device Log"
    name_plural = "Device Logs"
    icon = "fa-solid fa-clipboard-list"
    category = "Devices"

    column_list = [
        DeviceLog.id,
        DeviceLog.device,
        DeviceLog.action,
        DeviceLog.ip_address,
        DeviceLog.created_at,
    ]

    column_sortable_list = [DeviceLog.id, DeviceLog.created_at]
    column_default_sort = [(DeviceLog.id, True)]

    # Read-only
    can_create = False
    can_edit = False
    can_delete = False
