from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

PENDING = "PENDING"
SENT = "SENT"


@dataclass(frozen=True)
class User:
    user_id: str
    timezone: str
    quiet_start: str  # "HH:MM" local
    quiet_end: str  # "HH:MM" local
    channel: str = "push"


@dataclass(frozen=True)
class Alert:
    alert_id: int
    user_id: str
    symbol: str
    direction: str
    threshold: Decimal
    active: bool
    armed: bool


@dataclass(frozen=True)
class Delivery:
    delivery_id: int
    alert_id: int
    user_id: str
    message: str
    deliver_after: datetime
    status: str
