from decimal import ROUND_HALF_UP, Decimal

from ..errors import NotFound, Rejected
from ..models import ACTIVE, CHARGED, FAILED

PLATFORM_RATE = Decimal("0.05")
PROCESSING_RATE = Decimal("0.03")
PER_CHARGE_FEE = Decimal("0.20")
STRETCH_MULTIPLE = Decimal("1.5")
ZERO = Decimal("0.00")


def cents(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class SettlementService:
    def __init__(self, store, payments, clock):
        self._store = store
        self._payments = payments
        self._clock = clock

    def settle(self, campaign_id: str) -> dict:
        c = self._store.campaign(campaign_id)
        if c is None:
            raise NotFound(campaign_id)
        if c.settled or self._clock.now() < c.deadline:
            raise Rejected("campaign cannot be settled now")
        pledges = list(c.pledges.values())
        total = sum((p.amount for p in pledges), ZERO)
        funded = total > c.goal
        result = {"funded": funded, "pledged": total, "collected": ZERO, "platform_fee": ZERO, "processing_fee": ZERO,
                  "payout": ZERO, "stretch": False, "bonus_backers": []}
        if funded:
            attempted = 0
            for p in sorted(pledges, key=lambda p: p.pledge_id):
                attempted += 1
                if self._payments.charge(p.backer, p.amount):
                    p.status = CHARGED
                    result["collected"] += p.amount
                else:
                    p.status = FAILED
            result["platform_fee"] = cents(result["collected"] * PLATFORM_RATE)
            result["processing_fee"] = cents(result["collected"] * PROCESSING_RATE + PER_CHARGE_FEE * attempted)
            result["payout"] = result["collected"] - result["platform_fee"] - result["processing_fee"]
            if total >= c.goal * STRETCH_MULTIPLE:
                result["stretch"] = True
                result["bonus_backers"] = sorted({p.backer for p in pledges if p.tier == "DELUXE"})
        c.settled, c.result = True, result
        return result
