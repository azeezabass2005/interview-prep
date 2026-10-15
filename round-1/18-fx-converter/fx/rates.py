from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Tuple

MAX_AGE = timedelta(seconds=60)


class StaleRate(Exception):
    pass


class RateBook:
    def __init__(self, clock):
        self._clock = clock
        self._rates: Dict[str, Tuple[Decimal, datetime]] = {}

    def set(self, pair: str, rate, at: datetime = None) -> None:
        if len(pair) != 6:
            raise ValueError(f"bad pair {pair}")
        self._rates[pair] = (Decimal(rate), at or self._clock.now())

    def usd_per_unit(self, currency: str) -> Decimal:
        """How many USD one unit of `currency` is worth at mid."""
        if currency == "USD":
            return Decimal(1)
        for pair, (rate, at) in self._rates.items():
            base, quote = pair[:3], pair[3:]
            if base == currency and quote == "USD":
                return rate
            if base == "USD" and quote == currency:
                return rate
        raise KeyError(f"no rate for {currency}")
