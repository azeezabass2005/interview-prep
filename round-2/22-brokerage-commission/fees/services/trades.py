from datetime import datetime
from decimal import Decimal, InvalidOperation

from ..errors import InvalidState, NotFound, ValidationError
from ..models import ACTIVE, BUSTED, BUY, EQUITY, OPTION, SELL, Account, Trade
from ..store import InMemoryStore


class TradeService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def open_account(self, account_id: str, owner: str) -> Account:
        if self._store.account(account_id):
            raise ValidationError(f"account {account_id} exists")
        account = Account(account_id, owner)
        self._store.add_account(account)
        return account

    def record(self, payload: dict) -> Trade:
        try:
            trade = Trade(
                trade_id=str(payload["trade_id"]),
                account_id=payload["account_id"],
                asset_class=payload["asset_class"],
                side=payload["side"],
                quantity=int(payload["quantity"]),
                price=Decimal(str(payload["price"])),
                executed_at=datetime.fromisoformat(payload["executed_at"]),
            )
        except (KeyError, ValueError, InvalidOperation) as exc:
            raise ValidationError(f"bad trade: {exc}")
        if self._store.account(trade.account_id) is None:
            raise NotFound(f"account {trade.account_id}")
        if trade.asset_class not in (EQUITY, OPTION) or trade.side not in (BUY, SELL):
            raise ValidationError("unknown asset class or side")
        if trade.quantity <= 0 or trade.price <= 0:
            raise ValidationError("quantity and price must be positive")
        if self._store.trade(trade.trade_id):
            raise ValidationError(f"duplicate trade {trade.trade_id}")
        self._store.add_trade(trade)
        return trade

    def bust(self, trade_id: str) -> Trade:
        trade = self._store.trade(trade_id)
        if trade is None:
            raise NotFound(f"trade {trade_id}")
        if trade.status != ACTIVE:
            raise InvalidState("trade already busted")
        trade.status = BUSTED
        return trade
