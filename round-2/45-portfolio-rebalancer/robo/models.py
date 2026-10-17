from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, Set


@dataclass(frozen=True)
class Model:
    name: str
    weights: Dict[str, Decimal]


@dataclass
class Account:
    account_id: str
    model: str
    cash: Decimal
    holdings: Dict[str, int] = field(default_factory=dict)
    restricted: Set[str] = field(default_factory=set)


@dataclass(frozen=True)
class Trade:
    side: str
    symbol: str
    shares: int
