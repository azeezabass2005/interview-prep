from dataclasses import dataclass, field

BUY, SELL = "BUY", "SELL"
LIMIT, IOC = "LIMIT", "IOC"
NEW, PARTIAL, FILLED, CANCELLED = "NEW", "PARTIAL", "FILLED", "CANCELLED"


@dataclass(eq=False)
class Order:
    order_id: str
    member: str
    symbol: str
    side: str
    price: int
    quantity: int
    order_type: str = LIMIT
    filled: int = 0
    status: str = NEW
    seq: int = 0

    @property
    def remaining(self) -> int:
        # Return the quantity that has not yet been filled.
        return self.quantity - self.filled

    @property
    def is_live(self) -> bool:
        # Indicate whether the order is new or partially filled.
        return self.status in (NEW, PARTIAL)


@dataclass(frozen=True)
class Trade:
    symbol: str
    buy_order: str
    sell_order: str
    price: int
    quantity: int
