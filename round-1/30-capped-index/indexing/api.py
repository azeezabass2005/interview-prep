from datetime import date
from decimal import Decimal

from .errors import IndexError_
from .models import Security
from .services.rebalance import RebalanceService


class IndexApi:
    def __init__(self, service: RebalanceService):
        self._s = service

    def security(self, ticker, shares, free_float, price, listed_on):
        self._s.add_security(Security(ticker, int(shares), Decimal(str(free_float)), Decimal(str(price)),
                                      date.fromisoformat(listed_on)))
        return 201, {"ticker": ticker}

    def define(self, name, cap):
        try:
            return 201, {"name": self._s.define(name, cap).name}
        except IndexError_ as exc:
            return 400, {"error": str(exc)}

    def rebalance(self, name, on):
        try:
            r = self._s.rebalance(name, date.fromisoformat(on))
        except IndexError_ as exc:
            return 400, {"error": str(exc)}
        return 200, {"weights": {k: str(v) for k, v in sorted(r["weights"].items())}, "turnover": str(r["turnover"])}
