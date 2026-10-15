from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from ..errors import ExpenseError
from ..repositories.fx import FxRepository


class FxService:
    def __init__(self, rates: FxRepository):
        self._rates = rates

    def to_usd(self, amount: Decimal, currency: str, on: date) -> Decimal:
        if currency == "USD":
            return amount
        rate = self._rates.rate_on_or_before(currency, on)
        if rate is None:
            raise ExpenseError(f"no {currency} rate for {on}")
        return (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
