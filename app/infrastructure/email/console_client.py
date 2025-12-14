import logging

from app.infrastructure.email.client import EmailMessage


logger = logging.getLogger(__name__)


class ConsoleEmailClient:
    async def send(self, message: EmailMessage) -> None:
        logger.info(
            "[EMAIL MOCK] to=%s subject=%s body=%s",
            message.to,
            message.subject,
            message.body,
        )
