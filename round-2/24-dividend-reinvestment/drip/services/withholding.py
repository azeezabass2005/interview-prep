from decimal import ROUND_HALF_UP, Decimal

from ..config import CENT, DEFAULT_WITHHOLDING_RATE, WITHHOLDING_RATES
from ..models import Account


def withholding_rate(account: Account) -> Decimal:
    return WITHHOLDING_RATES.get(account.country.upper(), Decimal("0"))


def withholding(account: Account, gross: Decimal) -> Decimal:
    return (gross * withholding_rate(account)).quantize(CENT, rounding=ROUND_HALF_UP)
