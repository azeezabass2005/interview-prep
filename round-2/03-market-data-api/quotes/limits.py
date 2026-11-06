from .config import PLAN_LIMITS
from .ratelimit import FixedWindowLimiter


class PlanLimiter:
    """One fixed-window limiter per plan. Keys look like '<plan>:<who>'."""

    def __init__(self, clock):
        self._limiters = {plan: FixedWindowLimiter(clock, limit, 60) for plan, limit in PLAN_LIMITS.items()}

    def check(self, key: str):
        plan, _, _ = key.partition(":")
        return self._limiters.get(plan, self._limiters["basic"]).check(key)


def limit_key(request) -> str:
    principal = request.principal
    if principal is None:
        return f"basic:ip:{request.remote_addr}"
    plan = "pro" if principal.has_role("pro") else "basic"
    return f"{plan}:org:{principal.org_id}"
