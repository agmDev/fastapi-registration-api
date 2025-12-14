from app.settings import settings
from app.infrastructure.email.client import EmailClient
from app.infrastructure.email.console_client import ConsoleEmailClient


def get_email_client():
    if settings.email_provider_mode == "http":
        return EmailClient(
            base_url=str(settings.email_provider_base_url),
            timeout_seconds=settings.email_provider_timeout_seconds,
        )
    return ConsoleEmailClient()
