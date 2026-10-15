from ..errors import InvalidAmount


def parse_amount(text) -> int:
    """'10.10' -> 1010 cents. Rejects non-positive amounts."""
    try:
        cents = int(float(text) * 100)
    except (TypeError, ValueError):
        raise InvalidAmount(f"not an amount: {text!r}")
    if cents <= 0:
        raise InvalidAmount("amount must be positive")
    return cents


def format_cents(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"
