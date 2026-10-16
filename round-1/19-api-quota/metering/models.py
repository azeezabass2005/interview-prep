from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, Optional

from .plans import Plan


@dataclass(frozen=True)
class Decision:
    allowed: bool
    retry_after: Optional[Decimal] = None
    reason: str = ""


@dataclass
class Client:
    client_id: str
    plan: Plan
    tokens: Decimal
    last_refill: Decimal
    usage: Dict[str, int] = field(default_factory=dict)
