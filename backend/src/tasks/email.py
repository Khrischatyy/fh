"""
Email tasks for Celery.
Handles sending various email notifications via SendGrid.
"""
from celery import shared_task
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content, Email, To

from src.config import settings


# Jinja2 environment for email templates
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
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
        unsubscribe_url=settings.unsubscribe_url
    )

    text_content = f"Welcome to Funny How, {firstname}! Start booking studios now."

    return send_email(email, "Welcome to Funny How", html_content, text_content)


@shared_task(name="send_welcome_email_owner")
def send_welcome_email_owner(email: str, firstname: str, lastname: str, reset_token: str) -> bool:
    """
    Send welcome email to new studio owner (WelcomeMailOwner equivalent).
    Sent after email verification for studio owners.
    Includes password reset link for setting up account.
    """
    # Generate password reset URL
    reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}&email={email}"

    # Render HTML template
    template = template_env.get_template("emails/welcome_owner.html")
    html_content = template.render(
        firstname=firstname,
        lastname=lastname,
        reset_url=reset_url,
        unsubscribe_url=settings.unsubscribe_url
    )

    text_content = f"Welcome to Funny How, {firstname}! Set your password: {reset_url}"

    return send_email(email, "Welcome to Funny How", html_content, text_content)


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
    """Send booking confirmation to customer."""
    html_content = f"""
    <html>
        <body>
            <h2>Booking Confirmed!</h2>
            <p>Hi {firstname},</p>
            <p>Your booking has been confirmed. Here are the details:</p>
            <ul>
                <li><strong>Studio:</strong> {booking_details.get('studio_name')}</li>
                <li><strong>Room:</strong> {booking_details.get('room_name')}</li>
                <li><strong>Date:</strong> {booking_details.get('date')}</li>
                <li><strong>Time:</strong> {booking_details.get('start_time')} - {booking_details.get('end_time')}</li>
                <li><strong>Amount:</strong> ${booking_details.get('amount')}</li>
            </ul>
            <p>We look forward to seeing you!</p>
        </body>
    </html>
    """

    return send_email(email, "Booking Confirmed - Funny How", html_content)


@shared_task(name="send_booking_confirmation_owner")
def send_booking_confirmation_owner(
    email: str,
    owner_name: str,
    booking_details: Dict[str, Any],
) -> bool:
    """Send booking notification to studio owner."""
    html_content = f"""
    <html>
        <body>
            <h2>New Booking Received!</h2>
            <p>Hi {owner_name},</p>
            <p>You have a new booking:</p>
            <ul>
                <li><strong>Customer:</strong> {booking_details.get('customer_name')}</li>
                <li><strong>Room:</strong> {booking_details.get('room_name')}</li>
                <li><strong>Date:</strong> {booking_details.get('date')}</li>
                <li><strong>Time:</strong> {booking_details.get('start_time')} - {booking_details.get('end_time')}</li>
                <li><strong>Amount:</strong> ${booking_details.get('amount')}</li>
            </ul>
        </body>
    </html>
    """

    return send_email(email, "New Booking - Funny How", html_content)


@shared_task(name="send_booking_cancellation")
def send_booking_cancellation(
    email: str,
    firstname: str,
    booking_details: Dict[str, Any],
) -> bool:
    """Send booking cancellation notification."""
    html_content = f"""
    <html>
        <body>
            <h2>Booking Cancelled</h2>
            <p>Hi {firstname},</p>
            <p>Your booking has been cancelled:</p>
            <ul>
                <li><strong>Studio:</strong> {booking_details.get('studio_name')}</li>
                <li><strong>Room:</strong> {booking_details.get('room_name')}</li>
                <li><strong>Date:</strong> {booking_details.get('date')}</li>
            </ul>
            <p>If you paid, a refund will be processed within 5-7 business days.</p>
        </body>
    </html>
    """

    return send_email(email, "Booking Cancelled - Funny How", html_content)
