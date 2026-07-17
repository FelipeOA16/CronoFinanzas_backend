"""
Email service â€” delivers HTML emails via Resend or logs to console (dev mode).

Configuration:
  EMAIL_PROVIDER=dev     â†’ Print links to console; nothing is sent (default).
  EMAIL_PROVIDER=resend  â†’ Send via Resend API (RESEND_API_KEY required).

Security:
  - Tokens are NEVER logged in production (resend mode).
  - RESEND_API_KEY is NEVER logged.
  - Only success/failure is logged in resend mode.
  - Full links are printed only in dev mode.
"""
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from app.core.config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

_executor = ThreadPoolExecutor(max_workers=2)


# â”€â”€ Resend sender (sync â€” runs in thread pool) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _send_via_resend(to_email: str, subject: str, html_body: str) -> None:
    import resend  # noqa: PLC0415 â€” lazy import keeps startup fast if unused

    resend.api_key = settings.RESEND_API_KEY  # type: ignore[assignment]
    params: resend.Emails.SendParams = {  # type: ignore[attr-defined]
        "from": settings.EMAIL_FROM,
        "to": [to_email],
        "subject": subject,
        "html": html_body,
    }
    resp = resend.Emails.send(params)  # type: ignore[attr-defined]
    logger.info("[EMAIL] Sent via Resend â€” id=%s to=%s", resp.get("id"), to_email)


# â”€â”€ Internal dispatcher â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

async def _dispatch(to_email: str, subject: str, html_body: str, dev_link: str) -> None:
    """Route to Resend or dev-console based on EMAIL_PROVIDER."""
    if settings.EMAIL_PROVIDER != "resend":
        # Dev mode: show the clickable link so developers can test locally.
        logger.info(
            "\n"
            "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—\n"
            "â•‘  [EMAIL DEV â€” no real sending]                           â•‘\n"
            "â•‘  To      : %-46sâ•‘\n"
            "â•‘  Subject : %-46sâ•‘\n"
            "â•‘  Link    : %-46sâ•‘\n"
            "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•",
            to_email,
            subject,
            dev_link,
        )
        return

    if not settings.RESEND_API_KEY:
        logger.error(
            "[EMAIL] EMAIL_PROVIDER=resend but RESEND_API_KEY is not configured. "
            "Set RESEND_API_KEY in your environment."
        )
        return

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            _executor, _send_via_resend, to_email, subject, html_body
        )
    except Exception as exc:
        # Log error type only â€” never log API keys or token values.
        logger.error(
            "[EMAIL] Resend delivery failed for %s â€” %s: %s",
            to_email,
            type(exc).__name__,
            str(exc),
        )


# â”€â”€ Public API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

async def send_reset_password_email(to_email: str, token: str) -> None:
    """Send a password-reset email with a time-limited link (1 hour TTL)."""
    reset_url = f"{settings.APP_FRONTEND_URL}/reset-password?token={token}"
    subject = "Restablece tu contraseÃ±a â€” CronoFinanzas"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;padding:24px">
      <h2 style="color:#1565C0">CronoFinanzas</h2>
      <p>Recibimos una solicitud para restablecer la contrase&ntilde;a de tu cuenta.</p>
      <p>Haz clic en el bot&oacute;n para crear una nueva contrase&ntilde;a.
         El enlace expira en <strong>1 hora</strong>.</p>
      <p style="text-align:center;margin:32px 0">
        <a href="{reset_url}"
           style="background:#1565C0;color:#fff;padding:14px 28px;border-radius:6px;
                  text-decoration:none;font-weight:bold">
          Restablecer contrase&ntilde;a
        </a>
      </p>
      <p style="color:#888;font-size:13px">
        Si no solicitaste este cambio, ignora este correo.
        Tu contrase&ntilde;a seguir&aacute; siendo la misma.
      </p>
      <hr style="border:none;border-top:1px solid #eee;margin:24px 0">
      <p style="color:#aaa;font-size:12px">
        &iquest;El bot&oacute;n no funciona? Copia y pega este enlace en tu navegador:<br>
        <a href="{reset_url}" style="color:#1565C0;word-break:break-all">{reset_url}</a>
      </p>
    </div>
    """
    logger.info("[EMAIL] Queuing reset-password email to %s", to_email)
    await _dispatch(to_email, subject, html, reset_url)


async def send_verification_email(to_email: str, token: str) -> None:
    """Send an email-verification email with a time-limited link (24 hour TTL)."""
    verify_url = f"{settings.APP_FRONTEND_URL}/verify-email?token={token}"
    subject = "Verifica tu correo electr\u00f3nico \u2014 CronoFinanzas"
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;padding:24px">
      <h2 style="color:#1565C0">CronoFinanzas</h2>
      <p>&iexcl;Gracias por registrarte! Confirma tu direcci&oacute;n de correo electr&oacute;nico
         para activar todas las funciones de tu cuenta.</p>
      <p style="text-align:center;margin:32px 0">
        <a href="{verify_url}"
           style="background:#2E7D32;color:#fff;padding:14px 28px;border-radius:6px;
                  text-decoration:none;font-weight:bold">
          Verificar correo
        </a>
      </p>
      <p style="color:#888;font-size:13px">
        Este enlace expira en <strong>24 horas</strong>.
        Si no creaste esta cuenta, ignora este correo.
      </p>
      <hr style="border:none;border-top:1px solid #eee;margin:24px 0">
      <p style="color:#aaa;font-size:12px">
        &iquest;El bot&oacute;n no funciona? Copia y pega este enlace en tu navegador:<br>
        <a href="{verify_url}" style="color:#1565C0;word-break:break-all">{verify_url}</a>
      </p>
    </div>
    """
    logger.info("[EMAIL] Queuing verification email to %s", to_email)
    await _dispatch(to_email, subject, html, verify_url)
