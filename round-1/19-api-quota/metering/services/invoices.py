from decimal import ROUND_HALF_UP, Decimal

from ..models import Client
from . import meter


def invoice(client: Client, month: str) -> dict:
    used = meter.usage(client, month)
    plan = client.plan
    overage_units = used if used > plan.allowance else 0
    overage = (overage_units * plan.overage_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {"client": client.client_id, "month": month, "plan": plan.name, "units": used,
            "overage_units": overage_units, "fee": str(plan.monthly_fee), "overage": str(overage),
            "total": str(plan.monthly_fee + overage)}
