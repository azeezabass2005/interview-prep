from datetime import datetime
from decimal import Decimal

from .errors import ShippingError
from .services.checkout import parse_packages, quote


class ShippingApi:
    def quote(self, body: dict):
        try:
            q = quote(parse_packages(body["packages"]), int(body["zone"]), bool(body.get("residential")),
                      Decimal(str(body.get("subtotal", "0"))), Decimal(str(body.get("discount", "0"))),
                      datetime.fromisoformat(body["ordered_at"]))
        except ShippingError as exc:
            return exc.status, {"error": str(exc)}
        return 200, {"carrier": q["carrier"], "shipping": str(q["shipping"]),
                     "rates": {c: str(v) for c, v in q["rates"].items()}, "delivery": q["delivery"].isoformat()}
