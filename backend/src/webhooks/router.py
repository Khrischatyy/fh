"""Webhook handlers for external services."""

import logging
import stripe
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.config import settings
from src.devices.repository import DeviceRepository
from src.devices.service import DeviceService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


def get_device_service(db: AsyncSession = Depends(get_db)) -> DeviceService:
    """Dependency to get device service."""
    repository = DeviceRepository(db)
    return DeviceService(repository)


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Stripe webhook events.

    Currently handles:
    - checkout.session.completed: For device unlock payments via Cash App

    Stripe sends webhooks to this endpoint when payment events occur.
    The webhook signature is verified to ensure the request is from Stripe.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        logger.warning("Stripe webhook received without signature header")
        raise HTTPException(status_code=400, detail="Missing Stripe signature")

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.stripe_webhook_secret
        )
    except ValueError as e:
        logger.error(f"Invalid Stripe webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.SignatureVerificationError as e:
        logger.error(f"Invalid Stripe webhook signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    event_type = event["type"]
    logger.info(f"Stripe webhook received: {event_type}")

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        await handle_checkout_session_completed(session, db)
    else:
        logger.info(f"Unhandled Stripe event type: {event_type}")

    return {"status": "success"}


async def handle_checkout_session_completed(session: dict, db: AsyncSession):
    """
    Handle checkout.session.completed event.

    For device unlock payments:
    - Updates DeviceUnlockSession status to 'paid'
    - Sets expiration time (1 hour from now)
    - Logs the unlock action

    For regular booking payments:
    - Currently not handled here (uses redirect-based flow)
    """
    metadata = session.get("metadata", {})
    payment_type = metadata.get("type")

    if payment_type == "device_unlock":
        # This is a device unlock payment
        stripe_session_id = session.get("id")
        payment_intent_id = session.get("payment_intent")

        logger.info(f"Processing device unlock payment: {stripe_session_id}")

        try:
            # Get service
            repository = DeviceRepository(db)
            service = DeviceService(repository)

            # Process the unlock payment
            await service.process_unlock_payment(stripe_session_id, payment_intent_id)

            logger.info(f"Device unlock payment processed successfully: {stripe_session_id}")

        except Exception as e:
            logger.error(f"Error processing device unlock payment: {e}")
            # Don't raise - Stripe will retry if we return error
            # But we should log and investigate

    else:
        # Regular booking payment or other type
        # Currently handled via redirect flow, but we could add webhook handling here
        logger.info(f"Checkout session completed for type: {payment_type or 'unknown'}")
