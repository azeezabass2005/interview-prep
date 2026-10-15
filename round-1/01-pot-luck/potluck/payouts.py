from collections import defaultdict

from .config import TIER_SHARES
from .matching import count_matches
from .models import Draw, Payout, PayoutPlan


def build_payout_plan(draw: Draw) -> PayoutPlan:
    """Group entries by match tier and split each tier's share among its winners."""
    winners_by_tier = defaultdict(list)
    for entry in draw.entries:
        matches = count_matches(entry.code, draw.winning_code)
        if TIER_SHARES.get(matches, 0) > 0:
            winners_by_tier[matches].append(entry)

    plan = PayoutPlan(draw_number=draw.draw_number)
    remaining = draw.pot_cents

    for tier in sorted(winners_by_tier):
        winners = winners_by_tier[tier]
        tier_amount = min(draw.pot_cents * TIER_SHARES[tier] // 100, remaining)
        per_winner = tier_amount // len(winners)
        for entry in winners:
            plan.payouts.append(Payout(entry.entry_id, entry.participant, tier, per_winner))
            plan.total_awarded_cents += per_winner
        remaining -= per_winner * len(winners)

    plan.rollover_cents = draw.pot_cents - plan.total_awarded_cents
    return plan
