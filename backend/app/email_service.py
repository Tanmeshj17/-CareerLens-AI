"""
Email service for CareerLens AI.

Supports multiple delivery mechanisms:
1. SMTP (e.g. Gmail App Password, Outlook, Custom SMTP):
   - SMTP_USER / EMAIL_USER
   - SMTP_PASSWORD / EMAIL_PASSWORD / GMAIL_APP_PASSWORD
   - SMTP_HOST (defaults to smtp.gmail.com)
   - SMTP_PORT (defaults to 587)
   - Works for ANY email address worldwide without domain verification.

2. Resend API (via Resend SDK / REST API):
   - RESEND_API_KEY / EMAIL_API_KEY
   - EMAIL_FROM (defaults to CareerLens AI <onboarding@resend.dev>)
   - Note: Resend testing domain (onboarding@resend.dev) only allows sending to the account owner's email.
     To send to all recipients without SMTP, verify your custom domain at resend.com/domains.

3. Development / Sandbox Fallback:
   - If no provider is configured or delivery fails, returns False so the API can safely provide the direct reset link fallback.
"""
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger("email_service")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
EMAIL_API_KEY = os.getenv("RESEND_API_KEY") or os.getenv("EMAIL_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "CareerLens AI <onboarding@resend.dev>")

# SMTP Configurations (e.g. Gmail SMTP)
SMTP_USER = os.getenv("SMTP_USER") or os.getenv("EMAIL_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") or os.getenv("EMAIL_PASSWORD") or os.getenv("GMAIL_APP_PASSWORD", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))


def _send_via_smtp(to: str, subject: str, html: str) -> bool:
    """Send email via standard SMTP (e.g. Gmail SMTP with App Password)."""
    if not SMTP_USER or not SMTP_PASSWORD:
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SMTP_USER
        msg["To"] = to
        msg.attach(MIMEText(html, "html"))

        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            server.starttls()

        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [to], msg.as_string())
        server.quit()
        logger.info(f"EMAIL SENT via SMTP: to={to} subject='{subject}'")
        return True
    except Exception as exc:
        logger.warning(f"SMTP send failed to {to}: {exc}")
        return False


def _send_via_resend(to: str, subject: str, html: str) -> bool:
    """Send an email using Resend SDK. Returns True on success, False if blocked or failed."""
    if not EMAIL_API_KEY or EMAIL_API_KEY.startswith("re_fake_"):
        logger.info(f"[MOCKED RESEND] EMAIL SKIPPED to={to} subject='{subject}'")
        return False

    try:
        import resend
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
        logger.warning("Resend SDK not installed. Skipping Resend send.")
        return False
    except Exception as exc:
        logger.warning(f"Resend send failed to {to}: {exc}")
        # Note: Resend test sandbox only permits sending to the account owner's email address
        return False


def send_email_message(to: str, subject: str, html: str) -> bool:
    """Try SMTP first if configured, then Resend. Returns True if successfully sent."""
    # 1. Try SMTP if configured
    if SMTP_USER and SMTP_PASSWORD:
        if _send_via_smtp(to, subject, html):
            return True

    # 2. Try Resend if configured
    if EMAIL_API_KEY and not EMAIL_API_KEY.startswith("re_fake_"):
        if _send_via_resend(to, subject, html):
            return True

    return False


def send_verification_email(to: str, verification_url: str) -> bool:
    """
    Send an email verification link to a user.
    """
    subject = "Verify your CareerLens AI account"
    html = f"""
    <div style="font-family:'Plus Jakarta Sans',sans-serif,Arial;max-width:520px;margin:0 auto;padding:24px;border:1px solid #e2e8f0;rounded:16px;">
      <h2 style="color:#0050cb;margin-bottom:8px;">Welcome to CareerLens AI</h2>
      <p style="color:#475569;font-size:14px;line-height:1.6;">Click the button below to verify your email address and activate your account:</p>
      <div style="margin:24px 0;">
        <a href="{verification_url}"
           style="display:inline-block;padding:14px 28px;background:linear-gradient(135deg,#0050cb,#3b82f6);
                  color:#ffffff;border-radius:10px;text-decoration:none;font-weight:bold;font-size:14px;">
          Verify Email Address
        </a>
      </div>
      <p style="color:#94a3b8;font-size:12px;margin-top:24px;">
        This link expires in 24 hours. If you did not create an account, you can safely ignore this email.
      </p>
      <p style="color:#94a3b8;font-size:11px;word-break:break-all;">
        Direct URL: {verification_url}
      </p>
    </div>
    """

    if ENVIRONMENT != "production" and not (SMTP_USER or EMAIL_API_KEY):
        logger.info(f"[DEVELOPMENT] Verification URL for {to}: {verification_url}")
        return False

    return send_email_message(to, subject, html)


def send_password_reset_email(to: str, reset_url: str) -> bool:
    """
    Send a password reset link to a user.
    """
    subject = "Reset your CareerLens AI password"
    html = f"""
    <div style="font-family:'Plus Jakarta Sans',sans-serif,Arial;max-width:520px;margin:0 auto;padding:24px;border:1px solid #e2e8f0;border-radius:16px;">
      <h2 style="color:#0050cb;margin-bottom:8px;">Password Reset Request</h2>
      <p style="color:#475569;font-size:14px;line-height:1.6;">We received a request to reset the password for your CareerLens AI account.</p>
      <div style="margin:24px 0;">
        <a href="{reset_url}"
           style="display:inline-block;padding:14px 28px;background:linear-gradient(135deg,#0050cb,#3b82f6);
                  color:#ffffff;border-radius:10px;text-decoration:none;font-weight:bold;font-size:14px;">
          Reset Password
        </a>
      </div>
      <p style="color:#94a3b8;font-size:12px;margin-top:24px;">
        This link expires in 1 hour. If you did not request a password reset, you can safely ignore this email.
      </p>
      <p style="color:#94a3b8;font-size:11px;word-break:break-all;">
        Direct URL: {reset_url}
      </p>
    </div>
    """

    if ENVIRONMENT != "production" and not (SMTP_USER or EMAIL_API_KEY):
        logger.info(f"[DEVELOPMENT] Password reset URL for {to}: {reset_url}")
        return False

    return send_email_message(to, subject, html)
