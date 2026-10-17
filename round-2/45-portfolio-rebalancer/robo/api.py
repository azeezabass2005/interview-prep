from .errors import RoboError
from .services.accounts import AccountService
from .services.planner import plan
from .services.prices import PriceService
from .store import InMemoryStore


class RoboApi:
    def __init__(self, store: InMemoryStore, accounts: AccountService, prices: PriceService):
        self._store = store
        self._accounts = accounts
        self._prices = prices

    def _call(self, fn, ok=200):
        try:
            return ok, fn()
        except RoboError as exc:
            return exc.status, {"error": str(exc)}

    def model(self, name: str, weights: dict):
        return self._call(lambda: {"model": self._accounts.add_model(name, weights).name}, 201)

    def price(self, symbol: str, price):
        self._prices.set(symbol, price)
        return 200, {"symbol": symbol}

    def open(self, body: dict):
        return self._call(lambda: {"account_id": self._accounts.open(body["account_id"], body["model"], body["cash"],
                                                                     body.get("holdings", {}), body.get("restricted", [])).account_id}, 201)

    def plan(self, account_id: str):
        def go():
            account = self._accounts.get(account_id)
            return {"trades": [[t.side, t.symbol, t.shares] for t in plan(account, self._store.models[account.model], self._prices)]}
        return self._call(go)
