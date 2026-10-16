from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Quote:
    symbol: str
    bid: Decimal
    ask: Decimal
    last: Decimal
    timestamp: float
    stale: bool = False

    @property
    def spread(self) -> Decimal:
        return self.ask - self.bid


@dataclass(frozen=True)
class VenueQuote:
    venue: str
    symbol: str
    bid: Decimal
    ask: Decimal
    timestamp: float
