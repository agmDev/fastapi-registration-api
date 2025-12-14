import httpx
from dataclasses import dataclass

from app.infrastructure.email.exceptions import EmailProviderUnavailable


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    body: str
    sender: str


class EmailClient:
    """
    Third-party email provider accessed through HTTP API.
    This client is intentionally thin and mockable.
    """
    def __init__(self, base_url: str, timeout_seconds: float):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    async def send(self, message: EmailMessage) -> None:
        payload = {
            "from": message.sender,
            "to": message.to,
            "subject": message.subject,
            "body": message.body,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(f"{self._base_url}/send", json=payload)
                resp.raise_for_status()
        except (httpx.TimeoutException, httpx.TransportError) as e:
            raise EmailProviderUnavailable(str(e)) from e
        except httpx.HTTPStatusError as e:
            raise EmailProviderUnavailable(f"Email provider error: {e.response.status_code}") from e
