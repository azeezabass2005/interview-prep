from .errors import Rejected
from .models import BUY, IOC, LIMIT, SELL

LISTED = {"ABC", "XYZ", "QQQ"}


def validate(payload: dict) -> dict:
    # Normalize order fields and reject malformed or unsupported order values.
    try:
        price = int(payload["price"])
        quantity = int(payload["quantity"])
        side = payload["side"]
        symbol = payload["symbol"].upper()
        order_type = payload.get("type", LIMIT)
    except (KeyError, TypeError, ValueError) as exc:
        raise Rejected(f"malformed order: {exc}")
    if symbol not in LISTED:
        raise Rejected(f"unknown symbol {symbol}")
    if side not in (BUY, SELL) or order_type not in (LIMIT, IOC):
        raise Rejected("bad side or type")
    if price <= 0 or quantity <= 0:
        raise Rejected("price and quantity must be positive")
    return {"price": price, "quantity": quantity, "side": side, "symbol": symbol, "order_type": order_type}
