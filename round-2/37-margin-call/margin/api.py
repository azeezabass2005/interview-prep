from datetime import date
from decimal import Decimal

from .errors import MarginError
from .models import Account
from .services.calls import CallService
from .services.liquidation import liquidation_plan
from .services.prices import PriceService
from .services.valuation import Valuation
from .store import InMemoryStore


class MarginApi:
    def __init__(self, store: InMemoryStore, prices: PriceService, valuation: Valuation, calls: CallService):
        self._store = store
        self._prices = prices
        self._valuation = valuation
        self._calls = calls

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except MarginError as exc:
            return exc.status, {"error": str(exc)}

    def add_security(self, symbol: str, asset_class: str):
        self._store.securities[symbol] = asset_class
        return 201, {"symbol": symbol}

    def price(self, symbol: str, on: str, price):
        return self._call(lambda: {"symbol": self._prices.publish(symbol, date.fromisoformat(on), price).symbol}, 201)

    def open_account(self, account_id: str, cash, positions: dict):
        def go():
            self._store.accounts[account_id] = Account(account_id, Decimal(str(cash)), dict(positions))
            return {"account_id": account_id}
        return self._call(go, 201)

    def deposit(self, account_id: str, on: str, amount):
        return self._call(lambda: {"amount": str(self._calls.deposit(account_id, date.fromisoformat(on), amount).amount)})

    def run(self, account_id: str, on: str):
        def go():
            d = date.fromisoformat(on)
            summary = self._valuation.summary(self._store.account(account_id), d)
            call = self._calls.run(account_id, d)
            body = {k: str(v) for k, v in summary.items()}
            body["call"] = None if call is None else {"amount": str(call.amount), "status": call.status}
            if call is not None and call.status == "OPEN":
                body["plan"] = liquidation_plan(self._valuation, self._store.account(account_id), d, call.amount)
            return body
        return self._call(go)

    def call_status(self, account_id: str):
        calls = self._store.calls.get(account_id, [])
        return 200, {"calls": [{"amount": str(c.amount), "status": c.status} for c in calls]}
