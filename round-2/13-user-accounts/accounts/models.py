from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class User:
    user_id: int
    email: str
    display_name: str
    password_hash: str
    salt: str
    failed_attempts: int
    locked_until: Optional[datetime]
    deleted_at: Optional[datetime]


@dataclass(frozen=True)
class ResetToken:
    token: str
    user_id: int
    created_at: datetime
    used_at: Optional[datetime]
