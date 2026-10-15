from datetime import date
from decimal import Decimal

from ..errors import PnlError
from ..repositories.market import FxRepository


class FxService:
    def __init__(self, rates: FxRepository):
        self._rates = rates

    def to_usd(self, amount: Decimal, currency: str, on: date) -> Decimal:
        if currency == "USD":
            return amount
        rate = self._rates.rate(currency, on)
        if rate is None:
            raise PnlError(f"no {currency} rate on {on}")
        return amount * rate
