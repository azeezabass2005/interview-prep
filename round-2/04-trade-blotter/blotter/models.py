from dataclasses import dataclass

from .config import MAX_QUANTITY


@dataclass
class Trade:
    id: str
    desk: str
    trader_id: str
    counterparty_id: str
    symbol: str
    side: str
    quantity: int
    price_cents: int
    status: str
    trade_date: str
    booked_at: str
    version: int = 1

    @property
    def signed_quantity(self) -> int:
        return self.quantity if self.side == "buy" else -self.quantity

    def amended(self, quantity: int | None, price_cents: int | None) -> "Trade":
        if self.status != "live":
            raise ValueError(f"cannot amend a {self.status} trade")
        new_qty = self.quantity if quantity is None else quantity
        new_price = self.price_cents if price_cents is None else price_cents
        if not 0 < new_qty <= MAX_QUANTITY:
            raise ValueError(f"quantity must be between 1 and {MAX_QUANTITY}")
        if new_price <= 0:
            raise ValueError("price must be positive")
        return Trade(self.id, self.desk, self.trader_id, self.counterparty_id, self.symbol, self.side, new_qty, new_price,
                     self.status, self.trade_date, self.booked_at, self.version + 1)


@dataclass
class Counterparty:
    id: str
    name: str
    lei: str
