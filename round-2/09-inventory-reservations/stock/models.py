from dataclasses import dataclass
from datetime import datetime

ACTIVE, RELEASED, SOLD = "ACTIVE", "RELEASED", "SOLD"


@dataclass(frozen=True)
class Sku:
    sku: str
    name: str
    on_hand: int
    reserved: int
    reorder_point: int
    is_bundle: bool = False

    @property
    def available(self) -> int:
        return self.on_hand - self.reserved


@dataclass(frozen=True)
class Reservation:
    reservation_id: int
    cart_id: str
    sku: str
    qty: int
    expires_at: datetime
    status: str
