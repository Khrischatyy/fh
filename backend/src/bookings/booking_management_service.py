"""
Booking management service - Additional booking operations for cancel, filter, history.
Laravel-compatible implementations for booking management endpoints.
"""
from datetime import datetime, date as date_type, time as time_type, timedelta
from typing import Optional, Dict, Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload, joinedload
import pytz

from src.bookings.models import Booking, BookingStatus
from src.bookings.repository import BookingRepository
from src.exceptions import NotFoundException, BadRequestException
from src.auth.models import User
from src.rooms.models import Room
from src.addresses.models import Address
from src.companies.models import Company


class BookingManagementService:
    """Service for booking management operations (cancel, filter, history)."""

    def __init__(self, repository: BookingRepository):
        self._repository = repository
        self._session = repository._session

    async def cancel_booking(self, booking_id: int, user_id: int) -> Dict[str, Any]:
        """
        Cancel a booking with refund (Laravel-compatible).

        Business rules:
        - Studio owner: Can cancel anytime
        - Customer: Can cancel only if more than 1 hour before start time
        - Only paid bookings (status_id=2) can be cancelled
        - Issues refund automatically
        - Updates status to cancelled (status_id=3)

        Args:
            booking_id: Booking ID to cancel
            user_id: User making the cancellation

        Returns:
            Dict with booking and refund info

        Raises:
            NotFoundException: If booking not found
            BadRequestException: If cancellation not allowed
        """
        # Find booking with relationships
        stmt = (
            select(Booking)
            .where(Booking.id == booking_id)
            .options(
                joinedload(Booking.room).joinedload(Room.address).joinedload(Address.company),
                joinedload(Booking.status),
                joinedload(Booking.user)
            )
        )
        result = await self._session.execute(stmt)
        booking = result.scalar_one_or_none()

        if not booking:
            raise NotFoundException(f"Booking with ID {booking_id} not found")

        # Get studio owner to check authorization
        from src.companies.models import AdminCompany

        stmt = select(AdminCompany).where(
            AdminCompany.company_id == booking.room.address.company_id
        ).options(selectinload(AdminCompany.admin))
        result = await self._session.execute(stmt)
        admin_company = result.scalar_one_or_none()

        if not admin_company or not admin_company.admin:
            raise BadRequestException("Studio owner not found")

        studio_owner = admin_company.admin
        is_studio_owner = (user_id == studio_owner.id)
        is_booking_owner = (booking.user_id == user_id)

        # Check authorization: user must be either studio owner OR booking owner
        if not is_studio_owner and not is_booking_owner:
            raise BadRequestException("You are not authorized to cancel this booking")

        # Check if booking is paid (status_id=2)
        if booking.status_id != 2:
            raise BadRequestException("Only paid bookings can be cancelled")

        # Apply time restrictions based on user role
        if not is_studio_owner:
            # Customer: Must cancel more than 1 hour before start time
            booking_datetime = datetime.combine(booking.date, booking.start_time)
            if booking.room and booking.room.address and booking.room.address.timezone:
                tz = pytz.timezone(booking.room.address.timezone)
                booking_datetime = tz.localize(booking_datetime)
            else:
                tz = pytz.UTC
                booking_datetime = pytz.UTC.localize(booking_datetime)

            now = datetime.now(tz)
            hours_until_booking = (booking_datetime - now).total_seconds() / 3600

            if hours_until_booking < 1:
                raise BadRequestException(
                    "Cannot cancel less than 1 hour before booking start time"
                )
        # Studio owner: No time restrictions (can cancel anytime)

        # Process refund
        from src.payments.service import PaymentService

        payment_service = PaymentService(self._session)

        try:
            refund_result = await payment_service.refund_payment(
                booking=booking,
                studio_owner=studio_owner
            )
        except Exception as e:
            raise BadRequestException(f"Failed to process refund: {str(e)}")

        # Update booking status to cancelled (status_id=3)
        booking.status_id = 3
        await self._session.commit()
        await self._session.refresh(booking)

        # Send cancellation email (background task)
        from src.tasks.email import send_booking_cancellation

        # Format booking details for email
        booking_details = {
            'studio_name': booking.room.address.company.name,
            'room_name': booking.room.name,
            'date': booking.date.strftime("%d %b %Y"),
            'start_time': booking.start_time.strftime("%H:%M"),
            'end_time': booking.end_time.strftime("%H:%M"),
        }

        send_booking_cancellation.delay(
            email=booking.user.email,
            firstname=booking.user.firstname,
            booking_details=booking_details
        )

        return {
            "booking": booking,
            "refund": refund_result
        }

    async def filter_bookings(
        self,
        user_id: int,
        status: Optional[str] = None,
        date: Optional[date_type] = None,
        time: Optional[time_type] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 15
    ) -> Dict[str, Any]:
        """
        Filter all bookings with pagination (Laravel-compatible).

        Returns all bookings (both past and future).

        Args:
            user_id: Current user ID
            status: Filter by status name
            date: Filter by specific date
            time: Filter where booking active at this time
            search: Search company name or address street
            page: Page number
            per_page: Items per page

        Returns:
            Paginated bookings with relationships
        """
        return await self._filter_bookings_base(
            user_id=user_id,
            booking_type="all",
            status=status,
            date=date,
            time=time,
            search=search,
            page=page,
            per_page=per_page
        )

    async def filter_history(
        self,
        user_id: int,
        status: Optional[str] = None,
        date: Optional[date_type] = None,
        time: Optional[time_type] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 15
    ) -> Dict[str, Any]:
        """
        Filter past bookings with pagination (Laravel-compatible).

        Returns bookings where start datetime < NOW.

        Args:
            user_id: Current user ID
            status: Filter by status name
            date: Filter by specific date
            time: Filter where booking active at this time
            search: Search company name or address street
            page: Page number
            per_page: Items per page

        Returns:
            Paginated bookings with relationships
        """
        return await self._filter_bookings_base(
            user_id=user_id,
            booking_type="history",
            status=status,
            date=date,
            time=time,
            search=search,
            page=page,
            per_page=per_page
        )

    async def _filter_bookings_base(
        self,
        user_id: int,
        booking_type: str,
        status: Optional[str] = None,
        date: Optional[date_type] = None,
        time: Optional[time_type] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 15
    ) -> Dict[str, Any]:
        """
        Base method for filtering bookings (future or history).

        Implements Laravel's booking filter logic with timezone awareness.
        """
        # Get user's company to check if they're a studio owner
        from src.companies.models import AdminCompany

        stmt = select(AdminCompany).where(AdminCompany.admin_id == user_id)
        result = await self._session.execute(stmt)
        admin_company = result.scalar_one_or_none()

        # Build base query
        # Show ALL bookings where user is involved:
        # 1. Bookings they made as a customer (Booking.user_id == user_id)
        # 2. Bookings at studios they own (Address.company_id == their company)
        conditions = [Booking.user_id == user_id]

        if admin_company:
            # Studio owner: ALSO show bookings at their studios
            conditions.append(Address.company_id == admin_company.company_id)

        stmt = (
            select(Booking)
            .join(Room, Booking.room_id == Room.id)
            .join(Address, Room.address_id == Address.id)
            .join(Company, Address.company_id == Company.id)
            .join(BookingStatus, Booking.status_id == BookingStatus.id)
            .where(or_(*conditions))
        )

        # Apply future/history filter with timezone
        # Laravel uses: CONCAT(date, ' ', start_time) >= NOW()
        # We'll use date + start_time comparison
        now = datetime.now()

        if booking_type == "future":
            # Future bookings: date > today OR (date = today AND start_time >= now)
            stmt = stmt.where(
                or_(
                    Booking.date > now.date(),
                    and_(
                        Booking.date == now.date(),
                        Booking.start_time >= now.time()
                    )
                )
            )
        elif booking_type == "history":
            # Past bookings: date < today OR (date = today AND start_time < now)
            stmt = stmt.where(
                or_(
                    Booking.date < now.date(),
                    and_(
                        Booking.date == now.date(),
                        Booking.start_time < now.time()
                    )
                )
            )
        # else: booking_type == "all" - no time filter applied

        # Apply optional filters
        if status:
            stmt = stmt.where(BookingStatus.name == status)

        if date:
            stmt = stmt.where(Booking.date == date)

        if time:
            # Filter where booking active at this time
            stmt = stmt.where(
                and_(
                    Booking.start_time <= time,
                    Booking.end_time >= time
                )
            )

        if search:
            # Search company name or address street (case-insensitive)
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Company.name.ilike(search_pattern),
                    Address.street.ilike(search_pattern)
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar()

        # Order by date and time descending (most recent first)
        stmt = stmt.order_by(Booking.date.desc(), Booking.start_time.desc())

        # Apply pagination
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)

        # Load relationships
        stmt = stmt.options(
            selectinload(Booking.room).selectinload(Room.address).selectinload(Address.company),
            selectinload(Booking.room).selectinload(Room.address).selectinload(Address.badges),
            selectinload(Booking.status),
            selectinload(Booking.user),
            selectinload(Booking.device)
        )

        # Execute query
        result = await self._session.execute(stmt)
        bookings = result.scalars().unique().all()

        # Format bookings
        bookings_data = []
        for booking in bookings:
            # Determine if current user is the studio owner of this booking
            is_studio_owner = (
                admin_company is not None and
                booking.room.address.company_id == admin_company.company_id
            )

            booking_dict = {
                "id": booking.id,
                "start_time": booking.start_time.strftime("%H:%M:%S"),
                "end_time": booking.end_time.strftime("%H:%M:%S"),
                "date": booking.date.strftime("%Y-%m-%d"),
                "room_id": booking.room_id,
                "user_id": booking.user_id,
                "status_id": booking.status_id,
                "device_id": booking.device_id,
                "is_studio_owner": is_studio_owner,  # Frontend uses this to show status/device controls
                "room": {
                    "id": booking.room.id,
                    "name": booking.room.name,
                    "address": {
                        "id": booking.room.address.id,
                        "street": booking.room.address.street,
                        "company": {
                            "id": booking.room.address.company.id,
                            "name": booking.room.address.company.name,
                            "slug": booking.room.address.company.slug,
                        },
                        "badges": [
                            {"id": badge.id, "name": badge.name}
                            for badge in booking.room.address.badges
                        ] if booking.room.address.badges else []
                    }
                },
                "status": {
                    "id": booking.status.id,
                    "name": booking.status.name
                },
                "device": {
                    "id": booking.device.id,
                    "name": booking.device.name,
                    "is_active": booking.device.is_active,
                    "is_blocked": booking.device.is_blocked
                } if booking.device else None,
                "created_at": booking.created_at.isoformat(),
                "updated_at": booking.updated_at.isoformat(),
            }

            # Include user info if viewing as studio owner
            if is_studio_owner and booking.user:
                booking_dict["user"] = {
                    "id": booking.user.id,
                    "firstname": booking.user.firstname,
                    "lastname": booking.user.lastname,
                    "email": booking.user.email,
                    "phone": booking.user.phone,
                }

            bookings_data.append(booking_dict)

        # Calculate last page (Laravel pagination format)
        last_page = (total + per_page - 1) // per_page if total > 0 else 1

        return {
            "current_page": page,
            "data": bookings_data,
            "per_page": per_page,
            "total": total,
            "last_page": last_page
        }
