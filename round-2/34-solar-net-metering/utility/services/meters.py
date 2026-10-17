from ..config import REGISTER_MAX
from ..errors import BillingError


def register_delta(previous: int, current: int) -> int:
    if not (0 <= previous < REGISTER_MAX and 0 <= current < REGISTER_MAX):
        raise BillingError("register value out of range")
    return current - previous
