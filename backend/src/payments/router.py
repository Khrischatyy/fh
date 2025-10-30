"""
Payment router - API endpoints for payment operations.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query, status

from src.payments.service import PaymentService
from src.payments.schemas import (
    PaymentSuccessRequest,
    PaymentSuccessResponse,
    CreateAccountResponse,
    RefreshAccountLinkResponse,
    BalanceResponse
)
from src.payments.gateways.stripe_gateway import StripeGateway
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.exceptions import BadRequestException, NotFoundException

router = APIRouter(tags=["Payments"])


@router.get(
    "/payment/success",
    response_model=PaymentSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm payment success",
    description="Verify and process successful payment after Stripe redirect."
)
async def confirm_payment_success(
    session_id: Annotated[str, Query(description="Stripe session ID")],
    booking_id: Annotated[int, Query(description="Booking ID", gt=0)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PaymentSuccessResponse:
    """
    Confirm and process successful payment.

    **Query Parameters:**
    - **session_id**: Stripe checkout session ID
    - **booking_id**: Booking ID

    **Returns:**
    - **success**: Payment confirmation status
    - **message**: Success/error message
    - **booking_id**: Booking ID

    **Business Rules:**
    - Verifies payment session with Stripe
    - Updates booking status to confirmed
    - Updates charge record
    - Updates studio balance
    - Sends confirmation emails
    """
    try:
        # Get booking to find studio owner
        from src.bookings.repository import BookingRepository
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from src.bookings.models import Booking
        from src.companies.models import AdminCompany

        booking_repo = BookingRepository(db)
        booking = await booking_repo.get_booking_by_id(booking_id)

        if not booking:
            raise NotFoundException("Booking not found")

        # Get studio owner
        stmt = (
            select(Booking)
            .where(Booking.id == booking_id)
            .options(
                selectinload(Booking.room).selectinload(lambda r: r.address).selectinload(lambda a: a.company)
            )
        )
        result = await db.execute(stmt)
        booking_full = result.scalar_one_or_none()

        if not booking_full or not booking_full.room.address.company:
            raise BadRequestException("Studio company not found")

        # Get admin/owner
        stmt_admin = (
            select(AdminCompany)
            .where(AdminCompany.company_id == booking_full.room.address.company_id)
            .options(selectinload(AdminCompany.admin))
        )
        result_admin = await db.execute(stmt_admin)
        admin_company = result_admin.scalar_one_or_none()

        if not admin_company or not admin_company.admin:
            raise BadRequestException("Studio owner not found")

        studio_owner = admin_company.admin

        # Process payment
        payment_service = PaymentService(db)

        result = await payment_service.process_payment_success(
            session_id=session_id,
            booking_id=booking_id,
            gateway_name=studio_owner.payment_gateway or 'stripe',
            studio_owner=studio_owner
        )

        # Commit transaction
        await db.commit()

        return PaymentSuccessResponse(
            success=result['success'],
            message=result['message'],
            booking_id=booking_id
        )

    except Exception as e:
        await db.rollback()
        return PaymentSuccessResponse(
            success=False,
            message=str(e),
            booking_id=booking_id
        )


@router.post(
    "/stripe/account",
    response_model=CreateAccountResponse,
    status_code=status.HTTP_200_OK,
    summary="Create Stripe Connect account",
    description="Create a Stripe Connect Express account for studio owner."
)
async def create_stripe_account(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CreateAccountResponse:
    """
    Create Stripe Connect Express account.

    **Returns:**
    - **url**: Account onboarding URL
    - **message**: Success message

    **Business Rules:**
    - Only for studio owners
    - Creates Express account if doesn't exist
    - Returns onboarding link
    - Sets payment_gateway to 'stripe'
    """
    gateway = StripeGateway(db)
    result = await gateway.create_account(current_user)

    await db.commit()

    return CreateAccountResponse(
        url=result['url']
    )


@router.post(
    "/stripe/account/refresh",
    response_model=RefreshAccountLinkResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Stripe account link",
    description="Refresh Stripe Connect account onboarding link."
)
async def refresh_stripe_account_link(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RefreshAccountLinkResponse:
    """
    Refresh Stripe account onboarding link.

    **Returns:**
    - **url**: Refreshed onboarding URL
    - **message**: Success message
    """
    gateway = StripeGateway(db)
    result = await gateway.refresh_account_link(current_user)

    return RefreshAccountLinkResponse(
        url=result['url']
    )


@router.get(
    "/stripe/balance",
    response_model=BalanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Stripe account balance",
    description="Retrieve Stripe Connect account balance."
)
async def get_stripe_balance(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BalanceResponse:
    """
    Get Stripe account balance.

    **Returns:**
    - **available**: Available balance
    - **pending**: Pending balance
    - **message**: Success message
    """
    gateway = StripeGateway(db)
    balance = await gateway.retrieve_balance(current_user)

    return BalanceResponse(
        available=balance.get('available', []),
        pending=balance.get('pending', []),
    )
