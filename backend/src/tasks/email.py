"""
Email tasks for Celery.
Handles sending various email notifications via SendGrid.
"""
from celery import shared_task
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content, Email, To, TrackingSettings, ClickTracking

from src.config import settings


# Jinja2 environment for email templates
# __file__ = /app/src/tasks/email.py
# Go up 3 levels: /app/src/tasks/ -> /app/src/ -> /app/ then add templates/
template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
template_env = Environment(loader=FileSystemLoader(template_dir))


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str = None,
) -> bool:
    """
    Send email using SendGrid API.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML body content
        text_content: Plain text body content (optional)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create SendGrid message
        message = Mail(
            from_email=Email(settings.mail_from_address, settings.mail_from_name),
            to_emails=To(to_email),
            subject=subject,
            html_content=Content("text/html", html_content)
        )

        # Add plain text content if provided
        if text_content:
            message.add_content(Content("text/plain", text_content))

        # Disable click tracking to prevent SendGrid from wrapping URLs
        message.tracking_settings = TrackingSettings()
        message.tracking_settings.click_tracking = ClickTracking(enable=False, enable_text=False)

        # Send email
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        response = sg.send(message)

        # Check response
        if response.status_code >= 200 and response.status_code < 300:
            print(f"Email sent successfully to {to_email}: {subject}")
            return True
        else:
            print(f"SendGrid error: {response.status_code} - {response.body}")
            return False

    except Exception as e:
        print(f"Error sending email via SendGrid: {e}")
        return False


@shared_task(name="send_verification_email")
def send_verification_email(user_id: int, email: str, firstname: str, lastname: str) -> bool:
    """
    Send email verification link (CustomVerifyEmail equivalent).
    Uses Laravel-style id/hash verification URL.
    """
    import hashlib

    # Generate Laravel-style verification URL with id and hash
    email_hash = hashlib.sha1(email.encode()).hexdigest()
    verification_url = f"{settings.frontend_url}/email/verify/{user_id}/{email_hash}"

    # Render HTML template
    template = template_env.get_template("emails/verify_email.html")
    html_content = template.render(
        firstname=firstname,
        lastname=lastname,
        verification_url=verification_url,
        unsubscribe_url=settings.unsubscribe_url
    )

    text_content = f"Welcome {firstname}! Verify your email: {verification_url}"

    return send_email(email, "Verify Email Address", html_content, text_content)


@shared_task(name="send_welcome_email")
def send_welcome_email(email: str, firstname: str, lastname: str) -> bool:
    """
    Send welcome email to new user (WelcomeMail equivalent).
    Sent after email verification for regular users.
    """
    # Render HTML template
    template = template_env.get_template("emails/welcome.html")
    html_content = template.render(
        firstname=firstname,
        lastname=lastname,
        unsubscribe_url=settings.unsubscribe_url,
        email_assets_base_url=settings.email_assets_base_url
    )

    text_content = f"Welcome to Funny How, {firstname}! Start booking studios now."

    return send_email(email, "Welcome to Funny How", html_content, text_content)


@shared_task(name="send_welcome_email_owner")
def send_welcome_email_owner(email: str, firstname: str, lastname: str) -> bool:
    """
    Send welcome email to new studio owner (WelcomeMailOwner equivalent).
    Sent when user selects studio_owner role.
    Simple welcome - full setup email comes after Stripe verification.
    """
    # Render HTML template
    template = template_env.get_template("emails/welcome_owner.html")
    html_content = template.render(
        firstname=firstname,
        lastname=lastname,
        unsubscribe_url=settings.unsubscribe_url,
        email_assets_base_url=settings.email_assets_base_url
    )

    text_content = f"Welcome to Funny How, {firstname}! Set up your studio in your dashboard."

    return send_email(email, "Welcome to Funny How", html_content, text_content)


@shared_task(name="send_stripe_verified_email")
def send_stripe_verified_email(email: str, firstname: str, lastname: str, studio_name: str) -> bool:
    """
    Send Stripe account verified email to studio owner.
    Sent when Stripe payouts are enabled and studio is ready to take bookings.
    Tony Soprano style: "You're ready to make money, now wait for customers."
    """
    # Dashboard URL
    dashboard_url = f"{settings.frontend_url}/dashboard"

    # Render HTML template
    template = template_env.get_template("emails/stripe_verified.html")
    html_content = template.render(
        firstname=firstname,
        lastname=lastname,
        studio_name=studio_name,
        dashboard_url=dashboard_url,
        unsubscribe_url=settings.unsubscribe_url,
        email_assets_base_url=settings.email_assets_base_url
    )

    text_content = f"Your payment account is verified, {firstname}! Your studio '{studio_name}' is live and ready to take bookings."

    return send_email(email, "You're Ready for Business - Funny How", html_content, text_content)


@shared_task(name="send_password_reset_email")
def send_password_reset_email(email: str, token: str) -> bool:
    """
    Send password reset link (ResetPasswordMail equivalent).
    Sent when user requests password reset.
    """
    # Generate password reset URL
    reset_url = f"{settings.frontend_url}/reset-password?token={token}&email={email}"

    # Render HTML template
    template = template_env.get_template("emails/reset_password.html")
    html_content = template.render(
        email=email,
        reset_url=reset_url,
        unsubscribe_url=settings.unsubscribe_url
    )

    text_content = f"Reset your password: {reset_url}"

    return send_email(email, "Reset Password Mail", html_content, text_content)


@shared_task(name="send_booking_confirmation")
def send_booking_confirmation(
    email: str,
    firstname: str,
    booking_details: Dict[str, Any],
) -> bool:
    """
    Send booking confirmation to customer (Tony Soprano style).
    Sent when payment is successfully processed and booking is confirmed.
    """
    # Render HTML template
    template = template_env.get_template("emails/booking_confirmed.html")
    html_content = template.render(
        firstname=firstname,
        studio_name=booking_details.get('studio_name'),
        room_name=booking_details.get('room_name'),
        studio_address=booking_details.get('studio_address'),
        booking_date=booking_details.get('date'),
        start_time=booking_details.get('start_time'),
        end_time=booking_details.get('end_time'),
        bookings_url=f"{settings.frontend_url}/bookings",
        unsubscribe_url=settings.unsubscribe_url,
        email_assets_base_url=settings.email_assets_base_url
    )

    text_content = f"Your booking at {booking_details.get('studio_name')} is confirmed for {booking_details.get('date')} at {booking_details.get('start_time')}."

    return send_email(email, "You're All Set - Booking Confirmed", html_content, text_content)


@shared_task(name="send_booking_confirmation_owner")
def send_booking_confirmation_owner(
    email: str,
    owner_name: str,
    booking_details: Dict[str, Any],
) -> bool:
    """
    Send booking notification to studio owner (Tony Soprano style).
    Sent when customer successfully pays and confirms a booking.
    """
    # Render HTML template
    template = template_env.get_template("emails/booking_confirmation_owner.html")
    html_content = template.render(
        owner_name=owner_name,
        customer_name=booking_details.get('customer_name'),
        studio_name=booking_details.get('studio_name'),
        room_name=booking_details.get('room_name'),
        booking_date=booking_details.get('date'),
        start_time=booking_details.get('start_time'),
        end_time=booking_details.get('end_time'),
        amount=booking_details.get('amount'),
        bookings_url=f"{settings.frontend_url}/bookings",
        unsubscribe_url=settings.unsubscribe_url,
        email_assets_base_url=settings.email_assets_base_url
    )

    text_content = f"New booking at {booking_details.get('studio_name')} from {booking_details.get('customer_name')} on {booking_details.get('date')}."

    return send_email(email, "You Got a Booking - Funny How", html_content, text_content)


@shared_task(name="send_booking_cancellation")
def send_booking_cancellation(
    email: str,
    firstname: str,
    booking_details: Dict[str, Any],
) -> bool:
    """
    Send booking cancellation notification (Tony Soprano style).
    Sent when user or owner cancels a booking.
    """
    # Render HTML template
    template = template_env.get_template("emails/booking_cancelled.html")
    html_content = template.render(
        firstname=firstname,
        studio_name=booking_details.get('studio_name'),
        room_name=booking_details.get('room_name'),
        booking_date=booking_details.get('date'),
        start_time=booking_details.get('start_time'),
        end_time=booking_details.get('end_time'),
        browse_url=f"{settings.frontend_url}/studios",
        unsubscribe_url=settings.unsubscribe_url
    )

    text_content = f"Your booking at {booking_details.get('studio_name')} has been cancelled. If you paid, a refund will be processed within 5-7 business days."

    return send_email(email, "Booking Cancelled - Funny How", html_content, text_content)


@shared_task(name="send_booking_expired_notification")
def send_booking_expired_notification(
    email: str,
    booking_data: Dict[str, Any],
) -> bool:
    """
    Send booking expiry notification (Tony Soprano style).

    Called when a booking expires due to non-payment.

    Args:
        email: User's email address
        booking_data: Dict with booking_id, studio_name, date, start_time, end_time, user_name
    """
    booking_id = booking_data.get('booking_id')
    studio_name = booking_data.get('studio_name', 'Unknown Studio')
    date = booking_data.get('date')
    start_time = booking_data.get('start_time')
    end_time = booking_data.get('end_time')
    user_name = booking_data.get('user_name', '')

    # Render HTML template
    template = template_env.get_template("emails/booking_expired.html")
    html_content = template.render(
        user_name=user_name,
        booking_id=booking_id,
        studio_name=studio_name,
        date=date,
        start_time=start_time,
        end_time=end_time,
        browse_url=f"{settings.frontend_url}/studios",
        unsubscribe_url=settings.unsubscribe_url
    )

    text_content = f"Your booking payment expired. Booking #{booking_id} at {studio_name} on {date} was automatically cancelled. You didn't pay within 30 minutes."

    return send_email(
        email,
        f"Booking Payment Expired - Booking #{booking_id}",
        html_content,
        text_content
    )
