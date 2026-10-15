from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Link:
    code: str
    target_url: str
    owner: str
    created_at: datetime
    expires_at: Optional[datetime]
    clicks: int

    def is_expired(self, now: datetime) -> bool:
        return self.expires_at is not None and now >= self.expires_at
