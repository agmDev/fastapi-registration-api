from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ActivationCode:
    user_id: int
    hashed_code: str
    expires_at: datetime
    used: bool
