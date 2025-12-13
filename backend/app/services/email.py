"""
Email Service for sending transactional emails.

Supports verification emails, notifications, and other email communications.
Uses SMTP with configurable providers (SendGrid, AWS SES, or standard SMTP).
"""

import os
import logging
from typing import Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import smtplib
import ssl

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending transactional emails.

    Supports multiple email providers through environment configuration.
    Falls back to console logging in development mode.
    """

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        base_url: Optional[str] = None,
        dev_mode: Optional[bool] = None,
    ):
        """
        Initialize email service with SMTP configuration.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port (usually 587 for TLS)
            smtp_username: SMTP authentication username
            smtp_password: SMTP authentication password
            from_email: Sender email address
            from_name: Sender display name
            base_url: Base URL for links in emails (e.g., https://gocart.com)
            dev_mode: If True, log emails instead of sending
        """
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = smtp_username or os.getenv("SMTP_USERNAME", "")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.from_email = from_email or os.getenv("FROM_EMAIL", "noreply@gocart.com")
        self.from_name = from_name or os.getenv("FROM_NAME", "Go, Cart!")
        self.base_url = base_url or os.getenv("BASE_URL", "http://localhost:3000")
        self.dev_mode = dev_mode if dev_mode is not None else (
            os.getenv("ENVIRONMENT", "development") == "development"
        )

        # Template directory
        self.template_dir = Path(__file__).parent.parent / "templates" / "email"

    def _load_template(self, template_name: str) -> str:
        """
        Load HTML email template from file.

        Args:
            template_name: Name of template file (e.g., 'verification.html')

        Returns:
            Template content as string
        """
        template_path = self.template_dir / template_name

        if not template_path.exists():
            logger.warning(f"Template {template_name} not found at {template_path}")
            return ""

        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()

    def _render_template(self, template_content: str, context: Dict[str, Any]) -> str:
        """
        Simple template rendering using string replacement.

        Args:
            template_content: HTML template content
            context: Dictionary of variables to replace (e.g., {'name': 'John'})

        Returns:
            Rendered HTML string
        """
        rendered = template_content
        for key, value in context.items():
            placeholder = "{{" + key + "}}"
            rendered = rendered.replace(placeholder, str(value))
        return rendered

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """
        Send email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_body: HTML email body
            text_body: Plain text fallback (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        # Development mode: log instead of sending
        if self.dev_mode or not self.smtp_username or not self.smtp_password:
            logger.info(f"[DEV MODE] Email to {to_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"HTML Body (first 200 chars): {html_body[:200]}...")
            return True

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            message["Subject"] = subject

            # Add text and HTML parts
            if text_body:
                part1 = MIMEText(text_body, "plain")
                message.attach(part1)

            part2 = MIMEText(html_body, "html")
            message.attach(part2)

            # Create secure SSL/TLS context
            context = ssl.create_default_context()

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {to_email}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {to_email}: {e}")
            return False

    def send_verification_email(
        self,
        to_email: str,
        verification_token: str,
        user_name: Optional[str] = None,
    ) -> bool:
        """
        Send email verification email to waitlist user.

        Args:
            to_email: Recipient email address
            verification_token: Unique verification token
            user_name: Optional user name for personalization

        Returns:
            True if sent successfully, False otherwise
        """
        # Generate verification URL
        verification_url = f"{self.base_url}/verify?token={verification_token}"

        # Load and render template
        template = self._load_template("verification.html")

        context = {
            "verification_url": verification_url,
            "user_name": user_name or "there",
            "support_email": self.from_email,
            "year": "2024",
        }

        html_body = self._render_template(template, context)

        # Plain text fallback
        text_body = f"""
Hi {context['user_name']},

Welcome to Go, Cart! Please verify your email address to join the waitlist.

Click the link below to verify:
{verification_url}

If you didn't sign up for Go, Cart!, you can safely ignore this email.

Thanks,
The Go, Cart! Team
        """.strip()

        # Send email
        subject = "Verify your email for Go, Cart!"
        return self._send_email(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )

    def send_welcome_email(
        self,
        to_email: str,
        user_name: Optional[str] = None,
        position: Optional[int] = None,
    ) -> bool:
        """
        Send welcome email after email verification (optional).

        Args:
            to_email: Recipient email address
            user_name: Optional user name
            position: Queue position

        Returns:
            True if sent successfully, False otherwise
        """
        subject = "You're on the list! Welcome to Go, Cart!"

        position_text = (
            f"You're #{position} on the waitlist!"
            if position
            else "You're on the waitlist!"
        )

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 0; background-color: #FAF7F5;">
    <div style="max-width: 600px; margin: 40px auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);">
        <div style="background: linear-gradient(135deg, #E85A4F 0%, #FF9472 100%); padding: 40px 20px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to Go, Cart! 🎉</h1>
        </div>
        <div style="padding: 40px 30px;">
            <p style="font-size: 18px; color: #2A2521; margin-top: 0;">Hi {user_name or 'there'},</p>
            <p style="font-size: 16px; color: #635A50; line-height: 1.6;">
                Thanks for verifying your email! {position_text}
            </p>
            <p style="font-size: 16px; color: #635A50; line-height: 1.6;">
                We're working hard to launch Go, Cart! and make grocery shopping effortless for everyone.
                We'll keep you updated on our progress.
            </p>
            <p style="font-size: 14px; color: #857A6E; margin-top: 30px;">
                Thanks,<br>
                The Go, Cart! Team
            </p>
        </div>
    </div>
</body>
</html>
        """

        text_body = f"""
Hi {user_name or 'there'},

Thanks for verifying your email! {position_text}

We're working hard to launch Go, Cart! and make grocery shopping effortless for everyone.
We'll keep you updated on our progress.

Thanks,
The Go, Cart! Team
        """.strip()

        return self._send_email(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )


# Singleton instance for easy import
_email_service_instance: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """
    Get or create email service singleton instance.

    Returns:
        EmailService instance
    """
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailService()
    return _email_service_instance
