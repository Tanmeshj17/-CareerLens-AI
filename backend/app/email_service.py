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
    """Send email via standard SMTP (e.g. Gmail SMTP with App Password).
    Works for ANY recipient email address worldwide.
    """
    smtp_user = (os.getenv("SMTP_USER") or os.getenv("EMAIL_USER") or "").strip()
    smtp_pass = (os.getenv("SMTP_PASSWORD") or os.getenv("EMAIL_PASSWORD") or os.getenv("GMAIL_APP_PASSWORD") or "").replace(" ", "").strip()
    smtp_host = (os.getenv("SMTP_HOST") or "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT") or "587")

    if not smtp_user or not smtp_pass:
        logger.warning("SMTP skipped: SMTP_USER or SMTP_PASSWORD not configured.")
        return False

    # Attempt standard delivery (try configured port, fallback to 465/587 if needed)
    ports_to_try = [smtp_port]
    if smtp_port != 465:
        ports_to_try.append(465)
    if smtp_port != 587:
        ports_to_try.append(587)

    for port in ports_to_try:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"CareerLens AI <{smtp_user}>"
            msg["To"] = to
            msg.attach(MIMEText(html, "html"))

            if port == 465:
                server = smtplib.SMTP_SSL(smtp_host, port, timeout=12)
            else:
                server = smtplib.SMTP(smtp_host, port, timeout=12)
                server.ehlo()
                server.starttls()
                server.ehlo()

            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to], msg.as_string())
            server.quit()
            logger.info(f"EMAIL SENT successfully via SMTP ({smtp_host}:{port}): to={to} subject='{subject}'")
            return True
        except smtplib.SMTPAuthenticationError as exc:
            logger.error(f"SMTP Authentication Error ({smtp_host}:{port}) — check your Gmail App Password: {exc}")
            return False  # Bad credentials, no need to retry other ports
        except Exception as exc:
            logger.warning(f"SMTP send attempt on port {port} failed: {exc}")
            continue

    logger.error(f"All SMTP attempts failed for {to}")
    return False


def _send_via_brevo(to: str, subject: str, html: str) -> bool:
    """Send an email using Brevo (formerly Sendinblue) HTTP REST API over port 443.
    Works seamlessly on all cloud hosts (Render, Vercel, AWS) and allows sending to ANY recipient email worldwide.
    """
    api_key = (os.getenv("BREVO_API_KEY") or os.getenv("SENDINBLUE_API_KEY") or "").strip()
    if not api_key:
        return False

    sender_email = (os.getenv("SMTP_USER") or os.getenv("EMAIL_USER") or "tanmeshj17@gmail.com").strip()
    sender_name = "CareerLens AI"

    import json
    import urllib.request

    try:
        url = "https://api.brevo.com/v3/smtp/email"
        payload = {
            "sender": {"name": sender_name, "email": sender_email},
            "to": [{"email": to}],
            "subject": subject,
            "htmlContent": html,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "CareerLens-AI/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=12) as response:
            if response.status in (200, 201, 202):
                res_body = json.loads(response.read().decode())
                logger.info(f"EMAIL SENT via Brevo: messageId={res_body.get('messageId', 'ok')} to={to}")
                return True
            else:
                logger.warning(f"Brevo responded with status {response.status}")
                return False
    except Exception as exc:
        logger.warning(f"Brevo send failed to {to}: {exc}")
        return False


def _send_via_resend(to: str, subject: str, html: str) -> bool:
    """Send an email using Resend SDK over HTTPS. Returns True on success, False if blocked or failed."""
    api_key = (os.getenv("RESEND_API_KEY") or os.getenv("EMAIL_API_KEY") or "").strip()
    from_email = os.getenv("EMAIL_FROM", "CareerLens AI <onboarding@resend.dev>").strip()

    if not api_key or api_key.startswith("re_fake_"):
        logger.info(f"[MOCKED RESEND] EMAIL SKIPPED to={to} subject='{subject}'")
        return False

    try:
        import resend
        resend.api_key = api_key
        params = {
            "from": from_email,
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
        return False


def send_email_message(to: str, subject: str, html: str) -> bool:
    """Try Brevo HTTP API (global reach) -> Resend HTTP API -> SMTP. Returns True if successfully sent."""
    # 1. Try Brevo HTTPS API first (allows sending to ANY recipient email worldwide)
    brevo_key = os.getenv("BREVO_API_KEY") or os.getenv("SENDINBLUE_API_KEY")
    if brevo_key:
        if _send_via_brevo(to, subject, html):
            return True

    # 2. Try Resend HTTPS API
    resend_key = os.getenv("RESEND_API_KEY") or os.getenv("EMAIL_API_KEY")
    if resend_key and not resend_key.startswith("re_fake_"):
        if _send_via_resend(to, subject, html):
            return True

    # 3. Try standard SMTP
    smtp_user = os.getenv("SMTP_USER") or os.getenv("EMAIL_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD") or os.getenv("EMAIL_PASSWORD") or os.getenv("GMAIL_APP_PASSWORD")
    if smtp_user and smtp_pass:
        if _send_via_smtp(to, subject, html):
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

    return send_email_message(to, subject, html)
