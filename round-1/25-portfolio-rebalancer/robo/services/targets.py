from decimal import Decimal
from typing import Dict

from ..models import Account, Model
from .prices import PriceService

CASH_BUFFER = Decimal("0.02")


def effective_weights(model: Model, restricted) -> Dict[str, Decimal]:
    return {s: w for s, w in model.weights.items() if s not in restricted}


def total_value(account: Account, prices: PriceService) -> Decimal:
    return account.cash + sum((n * prices.get(s) for s, n in account.holdings.items()), Decimal(0))


def target_values(account: Account, model: Model, prices: PriceService) -> Dict[str, Decimal]:
    investable = total_value(account, prices)
    weights = effective_weights(model, account.restricted)
    targets = {s: investable * w for s, w in weights.items()}
    for symbol in account.holdings:
        targets.setdefault(symbol, Decimal(0))
    return targets
