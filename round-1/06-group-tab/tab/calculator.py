from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from typing import List

from .allocation import allocate_proportionally, split_evenly
from .models import Bill, Breakdown, Transfer

TAX_RATE = Decimal("0.08875")
AUTO_GRATUITY_PERCENT = 20
AUTO_GRATUITY_PARTY_SIZE = 6


def _round_cents(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def compute_breakdown(bill: Bill) -> Breakdown:
    subtotals = defaultdict(int)
    for item in bill.items:
        for person, amount in split_evenly(item.price_cents, item.sharers).items():
            subtotals[person] += amount

    subtotal = sum(subtotals.values())
    tax = _round_cents(subtotal * TAX_RATE)
    discounted = subtotal - bill.coupon_cents

    party_size = len(subtotals)
    tip_percent = AUTO_GRATUITY_PERCENT if party_size > AUTO_GRATUITY_PARTY_SIZE else bill.tip_percent
    tip = _round_cents(Decimal(discounted + tax) * tip_percent / 100)

    total = discounted + tax + tip
    shares = allocate_proportionally(total, dict(subtotals))
    return Breakdown(dict(subtotals), subtotal, bill.coupon_cents, tax, tip_percent, tip, total, shares)


def settle_up(bill: Bill) -> List[Transfer]:
    breakdown = compute_breakdown(bill)
    return [
        Transfer(person, bill.payer, amount)
        for person, amount in sorted(breakdown.shares.items())
    ]
