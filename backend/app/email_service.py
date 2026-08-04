"""
Email service for CareerLens AI.

Supports two modes controlled by the ENVIRONMENT env variable:
  - development: logs verification/reset URLs to console (no real emails sent)
  - production:  sends real emails via Resend SDK if RESEND_API_KEY is configured

Provider-agnostic design:
  - RESEND_API_KEY / EMAIL_API_KEY — Resend API key (optional until configured)
  - EMAIL_FROM — Sender address (defaults to safe placeholder onboarding@resend.dev)
  - ENVIRONMENT — 'development' | 'production'
"""
import logging
import os

logger = logging.getLogger("email_service")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
EMAIL_API_KEY = os.getenv("RESEND_API_KEY") or os.getenv("EMAIL_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "CareerLens AI <onboarding@resend.dev>")


def _send_via_resend(to: str, subject: str, html: str) -> bool:
    """Send an email using Resend SDK. Returns True on success or graceful fallback."""
    try:
        import resend
        if not EMAIL_API_KEY or EMAIL_API_KEY.startswith("re_fake_"):
            logger.info(f"[MOCKED RESEND] EMAIL SKIPPED to={to} subject='{subject}'")
            try:
                with open("mock_email.txt", "w") as f:
                    f.write(html)
            except Exception:
                pass
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
        logger.warning("Resend SDK not installed. Skipping email send gracefully.")
        return True
    except Exception as exc:
        logger.warning(f"Resend send failed to {to}: {exc}. Skipping email send gracefully.")
        return True


def send_verification_email(to: str, verification_url: str) -> bool:
    """
    Send an email verification link to a new user.
    In development mode or when RESEND_API_KEY is missing, logs the URL and returns True.
    In production mode with RESEND_API_KEY set, sends via Resend SDK.
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
        return True

    if not EMAIL_API_KEY:
        logger.warning(
            f"[EMAIL SKIPPED] RESEND_API_KEY is missing. Verification link for {to}: {verification_url}"
        )
        return True

    return _send_via_resend(to, subject, html)


def send_password_reset_email(to: str, reset_url: str) -> bool:
    """
    Send a password reset link.
    In development mode or when RESEND_API_KEY is missing, logs the URL and returns True.
    In production mode with RESEND_API_KEY set, sends via Resend SDK.
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
        logger.warning(
            f"[EMAIL SKIPPED] RESEND_API_KEY is missing. Password reset link for {to}: {reset_url}"
        )
        return True

    return _send_via_resend(to, subject, html)
