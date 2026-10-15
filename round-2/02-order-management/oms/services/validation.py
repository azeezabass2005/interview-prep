from decimal import Decimal, InvalidOperation

from ..config import MAX_ORDER_QTY, SIDES, TICK_TABLE
from ..errors import ValidationError


def tick_for(price: float) -> float:
    for threshold, tick in TICK_TABLE:
        if price >= threshold:
            return tick
    raise ValidationError("price must be positive")


def validate_order(payload: dict) -> dict:
    for field in ("account", "symbol", "side", "quantity", "limit_price"):
        if field not in payload:
            raise ValidationError(f"missing field: {field}")
    if payload["side"] not in SIDES:
        raise ValidationError("side must be BUY or SELL")
    qty = payload["quantity"]
    if not isinstance(qty, int) or not 1 <= qty <= MAX_ORDER_QTY:
        raise ValidationError(f"quantity must be 1..{MAX_ORDER_QTY}")
    try:
        price = float(payload["limit_price"])
    except (TypeError, ValueError):
        raise ValidationError("limit_price must be a number")
    if price <= 0:
        raise ValidationError("limit_price must be positive")
    tick = tick_for(price)
    steps = price * round(1 / tick)
    if int(steps) != steps:
        raise ValidationError(f"price {payload['limit_price']} is not on a valid tick")
    try:
        limit = Decimal(str(payload["limit_price"]))
    except InvalidOperation:
        raise ValidationError("limit_price must be a number")
    return {"account": payload["account"], "symbol": payload["symbol"].upper(), "side": payload["side"],
            "quantity": qty, "limit_price": limit}
