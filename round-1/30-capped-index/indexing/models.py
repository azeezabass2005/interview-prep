from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Dict, List


@dataclass(frozen=True)
class Security:
    ticker: str
    shares: int
    free_float: Decimal
    price: Decimal
    listed_on: date


@dataclass
class IndexDefinition:
    name: str
    cap: Decimal
    history: List[Dict[str, Decimal]] = field(default_factory=list)
