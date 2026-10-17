from ..config import ENTRY_PRICE_CENTS
from ..models import ACTIVE, SETTLED
from ..store import InMemoryStore


def participant_statement(store: InMemoryStore, participant_id: str) -> dict:
    entries = store.entries_for_participant(participant_id)
    spent = ENTRY_PRICE_CENTS * sum(1 for e in entries if e.status == ACTIVE)
    won = 0
    draws = set()
    for entry in entries:
        draw = store.draw(entry.draw_id)
        if draw.status != SETTLED:
            continue
        draws.add(draw.number)
        won += store.settlement(draw.draw_id).amount_for(entry.entry_id)
    return {"participant_id": participant_id, "spent_cents": spent, "won_cents": won,
            "net_cents": won - spent, "draws_settled": sorted(draws)}


def draw_summary(store: InMemoryStore, draw_id: int) -> dict:
    draw = store.draw(draw_id)
    summary = {"draw": draw.number, "status": draw.status, "pot_cents": draw.pot_cents,
               "winning_code": draw.winning_code, "carried_in_cents": draw.carried_in_cents}
    settlement = store.settlement(draw_id)
    if settlement:
        by_tier = {}
        for payout in settlement.payouts:
            by_tier.setdefault(payout.matches, []).append(payout.amount_cents)
        summary["tiers"] = {tier: {"winners": len(v), "each_cents": v[0]} for tier, v in sorted(by_tier.items())}
        summary["rollover_cents"] = settlement.rollover_cents
    return summary
