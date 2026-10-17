from decimal import Decimal, InvalidOperation

from ..errors import NotFound, RoboError
from ..models import Account, Model
from ..store import InMemoryStore


class AccountService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def add_model(self, name: str, weights: dict) -> Model:
        try:
            parsed = {s: Decimal(str(w)) / 100 for s, w in weights.items()}
        except InvalidOperation:
            raise RoboError("weights must be numbers")
        if sum(parsed.values()) != 1 or any(w < 0 for w in parsed.values()):
            raise RoboError("weights must be non-negative and add up to 100")
        model = Model(name, parsed)
        self._store.models[name] = model
        return model

    def open(self, account_id: str, model: str, cash, holdings: dict, restricted=()) -> Account:
        if model not in self._store.models:
            raise NotFound(model)
        account = Account(account_id, model, Decimal(str(cash)), dict(holdings), set(restricted))
        self._store.accounts[account_id] = account
        return account

    def get(self, account_id: str) -> Account:
        account = self._store.accounts.get(account_id)
        if account is None:
            raise NotFound(account_id)
        return account
