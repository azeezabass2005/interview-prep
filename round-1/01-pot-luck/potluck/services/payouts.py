from typing import List

from ..config import TIER_SHARES
from ..matching import group_by_matches
from ..models import Draw, Entry, Payout, Settlement


def build_settlement(draw: Draw, entries: List[Entry]) -> Settlement:
    groups = group_by_matches(entries, draw.winning_code)
    remaining = draw.pot_cents
    payouts = []
    for tier in sorted(TIER_SHARES):
        winners = groups.get(tier, [])
        if not winners:
            continue
        entitlement = draw.pot_cents * TIER_SHARES[tier] // 100
        tier_amount = min(entitlement, remaining)
        each = tier_amount // len(winners)
        for entry in sorted(winners, key=lambda e: e.entry_id):
            payouts.append(Payout(entry.entry_id, entry.participant_id, tier, each))
        remaining -= each * len(winners)
    awarded = sum(p.amount_cents for p in payouts)
    return Settlement(draw.draw_id, tuple(payouts), awarded, draw.pot_cents - awarded)
