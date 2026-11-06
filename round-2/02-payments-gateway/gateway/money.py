from decimal import Decimal, InvalidOperation

from .errors import ValidationError

# ISO 4217 minor-unit exponents for the currencies we accept.
CURRENCY_EXPONENT = {"USD": 2, "EUR": 2, "GBP": 2, "CHF": 2, "JPY": 0, "KWD": 3}


def to_minor(amount: str, currency: str) -> int:
    """'12.34' USD -> 1234. Rejects more decimal places than the currency has."""
    if currency not in CURRENCY_EXPONENT:
        raise ValidationError(f"unsupported currency {currency}")
    try:
        value = Decimal(str(amount))
    except InvalidOperation as e:
        raise ValidationError("amount must be a decimal string") from e
    if value <= 0:
        raise ValidationError("amount must be positive")
    exponent = CURRENCY_EXPONENT[currency]
    if -value.as_tuple().exponent > exponent:
        raise ValidationError(f"{currency} amounts have at most {exponent} decimal places")
    return int(value * 100)


def to_major(minor: int, currency: str) -> str:
    exponent = CURRENCY_EXPONENT[currency]
    return f"{Decimal(minor) / (Decimal(10) ** exponent):.{exponent}f}"
