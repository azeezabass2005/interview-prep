from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import List

from ..config import CARRIERS, FREE_MAX_ZONE, FREE_THRESHOLD, PREFERRED
from ..errors import ShippingError
from ..models import Package
from .estimate import delivery_date
from .rating import order_rate


def parse_packages(raw) -> List[Package]:
    try:
        packages = [Package(*(Decimal(str(p[k])) for k in ("l", "w", "h", "lb"))) for p in raw]
    except (KeyError, InvalidOperation):
        raise ShippingError("packages need l, w, h and lb")
    if not packages or any(v <= 0 for p in packages for v in (p.length, p.width, p.height, p.weight)):
        raise ShippingError("at least one package with positive dimensions")
    return packages


def quote(packages: List[Package], zone: int, residential: bool, subtotal: Decimal, discount: Decimal,
          ordered_at: datetime) -> dict:
    rates = {c: order_rate(packages, c, zone, residential) for c in CARRIERS}
    carrier = min(rates, key=lambda c: (rates[c], c != PREFERRED))
    shipping = rates[carrier]
    if subtotal >= FREE_THRESHOLD and zone <= FREE_MAX_ZONE:
        shipping = Decimal("0.00")
    return {"carrier": carrier, "shipping": shipping, "rates": rates,
            "delivery": delivery_date(ordered_at, carrier)}
