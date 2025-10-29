"""
Email tasks for Celery.
Handles sending various email notifications.
"""
from celery import shared_task
from typing import Dict, Any
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import asyncio

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content, Email, To

from src.config import settings


# Jinja2 environment for email templates
template_env = Environment(loader=FileSystemLoader("templates"))


def send_email_sendgrid(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str = None,
) -> bool:
    """Send email using SendGrid API."""
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
            return True
        else:
            print(f"SendGrid error: {response.status_code} - {response.body}")
            return False

    except Exception as e:
        print(f"Error sending email via SendGrid: {e}")
        return False


async def send_email_smtp(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str = None,
) -> bool:
    """Send email using SMTP (fallback for local development)."""
    try:
        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.mail_from_name} <{settings.mail_from_address}>"
        message["To"] = to_email
        message["Subject"] = subject

        # Add plain text version
        if text_content:
            part1 = MIMEText(text_content, "plain")
            message.attach(part1)

        # Add HTML version
        part2 = MIMEText(html_content, "html")
        message.attach(part2)

        # Send email
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            use_tls=settings.smtp_tls,
        )

        return True
    except Exception as e:
        print(f"Error sending email via SMTP: {e}")
        return False


def send_email_sync(to_email: str, subject: str, html_content: str, text_content: str = None):
    """
    Synchronous wrapper for sending email.
    Uses SendGrid if API key is configured, otherwise falls back to SMTP.
    """
    # Use SendGrid if API key is configured
    if settings.sendgrid_api_key:
        return send_email_sendgrid(to_email, subject, html_content, text_content)
    else:
        # Fallback to SMTP (Mailtrap for local development)
        return asyncio.run(send_email_smtp(to_email, subject, html_content, text_content))


@shared_task(name="send_verification_email")
def send_verification_email(email: str, token: str, firstname: str) -> bool:
    """Send email verification link."""
    verification_url = f"{settings.cors_origins[0]}/verify-email?token={token}"

    html_content = f"""
    <html>
        <body>
            <h2>Welcome to Funny How, {firstname}!</h2>
            <p>Please verify your email address by clicking the link below:</p>
            <a href="{verification_url}">Verify Email</a>
            <p>If you didn't create an account, please ignore this email.</p>
        </body>
    </html>
    """

    text_content = f"Welcome {firstname}! Verify your email: {verification_url}"

    return send_email_sync(email, "Verify Your Email - Funny How", html_content, text_content)


@shared_task(name="send_welcome_email")
def send_welcome_email(email: str, firstname: str) -> bool:
    """Send welcome email to new user."""
    html_content = f"""
    <html>
        <body>
            <h2>Welcome to Funny How, {firstname}!</h2>
            <p>Thank you for joining our studio booking platform.</p>
            <p>You can now browse and book amazing studios for your projects.</p>
            <p>Happy booking!</p>
        </body>
    </html>
    """

    return send_email_sync(email, "Welcome to Funny How", html_content)


@shared_task(name="send_welcome_email_owner")
def send_welcome_email_owner(email: str, firstname: str) -> bool:
    """Send welcome email to new studio owner."""
    html_content = f"""
    <html>
        <body>
            <h2>Welcome to Funny How, {firstname}!</h2>
            <p>Thank you for joining as a studio owner.</p>
            <p>You can now list your studios and start receiving bookings.</p>
            <p>Get started by adding your first studio!</p>
        </body>
    </html>
    """

    return send_email_sync(email, "Welcome to Funny How - Studio Owner", html_content)


@shared_task(name="send_password_reset_email")
def send_password_reset_email(email: str, token: str, firstname: str) -> bool:
    """Send password reset link."""
    reset_url = f"{settings.cors_origins[0]}/reset-password?token={token}"

    html_content = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hi {firstname},</p>
            <p>You requested to reset your password. Click the link below to proceed:</p>
            <a href="{reset_url}">Reset Password</a>
            <p>If you didn't request this, please ignore this email.</p>
            <p>This link will expire in 1 hour.</p>
        </body>
    </html>
    """

    return send_email_sync(email, "Password Reset - Funny How", html_content)


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

    return send_email_sync(email, "Booking Confirmed - Funny How", html_content)


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

    return send_email_sync(email, "New Booking - Funny How", html_content)


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

    return send_email_sync(email, "Booking Cancelled - Funny How", html_content)
