"""
Email service for CareerLens AI.

Supports two modes controlled by the ENVIRONMENT env variable:
  - development: logs the verification URL to console (no real emails sent)
  - production:  sends real emails via the Resend SDK

Provider-agnostic design:
  - EMAIL_API_KEY  — Resend API key (or any future provider's key)
  - EMAIL_FROM     — Sender address (e.g. no-reply@yourdomain.com)
  - ENVIRONMENT    — 'development' | 'production'

To add a different email provider (SendGrid, SES, etc.) later,
only this module needs to change. main.py is not coupled to the provider.
"""
import logging
import os

logger = logging.getLogger("email_service")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
EMAIL_API_KEY = os.getenv("RESEND_API_KEY") or os.getenv("EMAIL_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "CareerLens AI <noreply@careerlens.ai>")


def _send_via_resend(to: str, subject: str, html: str) -> bool:
    """Send an email using Resend SDK. Returns True on success, False on error."""
    try:
        import resend
        if EMAIL_API_KEY.startswith("re_fake_"):
            logger.info(f"[MOCKED RESEND] EMAIL SENT to={to} subject='{subject}'")
            with open("mock_email.txt", "w") as f:
                f.write(html)
            return True

        resend.api_key = EMAIL_API_KEY
        params = {
            "from": EMAIL_FROM,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        response = resend.Emails.send(params)
        logger.info(f"EMAIL SENT via Resend: id={response.get('id', 'unknown')} to={to}")
        return True
    except ImportError:
        logger.error("Resend SDK not installed. Run: pip install resend")
        return False
    except Exception as exc:
        logger.error(f"Resend send failed to {to}: {exc}")
        return False


def send_verification_email(to: str, verification_url: str) -> bool:
    """
    Send an email verification link to a new user.
    In development mode, just logs the URL.
    In production mode, sends via Resend.
    """
    subject = "Verify your CareerLens AI account"
    html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:0 auto;">
      <h2 style="color:#4f46e5;">Welcome to CareerLens AI</h2>
      <p>Click the button below to verify your email address and activate your account:</p>
      <a href="{verification_url}"
         style="display:inline-block;padding:12px 24px;background:#4f46e5;
                color:#fff;border-radius:6px;text-decoration:none;font-weight:bold;">
        Verify Email
      </a>
      <p style="color:#6b7280;font-size:13px;margin-top:24px;">
        This link expires in 24 hours. If you did not create an account, ignore this email.
      </p>
      <p style="color:#9ca3af;font-size:12px;">
        Or copy this URL into your browser:<br>{verification_url}
      </p>
    </div>
    """

    if ENVIRONMENT != "production":
        logger.info(
            f"[DEVELOPMENT] Verification URL for {to}: {verification_url}"
        )
        return True  # Simulate success in dev

    if not EMAIL_API_KEY:
        logger.error(
            "EMAIL_API_KEY is not set. Cannot send verification email. "
            "Set ENVIRONMENT=development to fall back to console logging."
        )
        return False

    return _send_via_resend(to, subject, html)


def send_password_reset_email(to: str, reset_url: str) -> bool:
    """
    Send a password reset link.
    In development mode, just logs the URL.
    In production mode, sends via Resend.
    """
    subject = "Reset your CareerLens AI password"
    html = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:0 auto;">
      <h2 style="color:#4f46e5;">Password Reset Request</h2>
      <p>We received a request to reset the password for your CareerLens AI account.</p>
      <a href="{reset_url}"
         style="display:inline-block;padding:12px 24px;background:#4f46e5;
                color:#fff;border-radius:6px;text-decoration:none;font-weight:bold;">
        Reset Password
      </a>
      <p style="color:#6b7280;font-size:13px;margin-top:24px;">
        This link expires in 1 hour. If you didn't request a reset, you can safely ignore this.
      </p>
      <p style="color:#9ca3af;font-size:12px;">
        Or copy this URL into your browser:<br>{reset_url}
      </p>
    </div>
    """

    if ENVIRONMENT != "production":
        logger.info(f"[DEVELOPMENT] Password reset URL for {to}: {reset_url}")
        return True

    if not EMAIL_API_KEY:
        logger.error("EMAIL_API_KEY is not set. Cannot send password reset email.")
        return False

    return _send_via_resend(to, subject, html)
