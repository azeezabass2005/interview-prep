from decimal import Decimal, InvalidOperation
from typing import Dict, Iterable

from .errors import ValidationError
from .models import EQUAL, EXACT, PERCENT, SHARES


def split_equal(amount: int, people: Iterable[str]) -> Dict[str, int]:
    names = sorted(set(people))
    if not names:
        raise ValidationError("at least one participant")
    base = amount // len(names)
    return {name: base for name in names}


def split_exact(amount: int, exact: Dict[str, int]) -> Dict[str, int]:
    if any(v < 0 for v in exact.values()):
        raise ValidationError("negative share")
    if sum(exact.values()) != amount:
        raise ValidationError("exact shares must add up to the total")
    return dict(exact)


def _split_weighted(amount: int, weights: Dict[str, Decimal]) -> Dict[str, int]:
    total = sum(weights.values())
    exact = {name: Decimal(amount) * w / total for name, w in weights.items()}
    shares = {name: int(value) for name, value in exact.items()}
    leftover = amount - sum(shares.values())
    for name in sorted(shares)[:leftover]:
        shares[name] += 1
    return shares


def split_percent(amount: int, percents: Dict[str, str]) -> Dict[str, int]:
    try:
        values = {k: Decimal(str(v)) for k, v in percents.items()}
    except InvalidOperation:
        raise ValidationError("percentages must be numbers")
    if any(v < 0 for v in values.values()) or sum(values.values()) != 100:
        raise ValidationError("percentages must add up to 100")
    return _split_weighted(amount, values)


def split_shares(amount: int, weights: Dict[str, int]) -> Dict[str, int]:
    if not weights or any(int(w) < 0 for w in weights.values()) or sum(int(w) for w in weights.values()) == 0:
        raise ValidationError("weights must be non-negative and not all zero")
    return _split_weighted(amount, {k: Decimal(int(v)) for k, v in weights.items()})


def compute_shares(split_type: str, amount: int, details) -> Dict[str, int]:
    if amount <= 0:
        raise ValidationError("amount must be positive")
    if split_type == EQUAL:
        return split_equal(amount, details)
    if split_type == EXACT:
        return split_exact(amount, {k: int(v) for k, v in details.items()})
    if split_type == PERCENT:
        return split_percent(amount, details)
    if split_type == SHARES:
        return split_shares(amount, details)
    raise ValidationError(f"unknown split type {split_type}")
