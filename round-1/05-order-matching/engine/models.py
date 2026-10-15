from dataclasses import dataclass, field

BUY = "BUY"
SELL = "SELL"


@dataclass(eq=False)
class Order:
    order_id: str
    trader: str
    side: str
    price: int
    quantity: int
    remaining: int = field(init=False)

    def __post_init__(self):
        if self.side not in (BUY, SELL):
            raise ValueError(f"bad side {self.side}")
        if self.price <= 0 or self.quantity <= 0:
            raise ValueError("price and quantity must be positive")
        self.remaining = self.quantity


@dataclass(frozen=True)
class Fill:
    incoming_id: str
    resting_id: str
    price: int
    quantity: int
