from decimal import Decimal as D

from rebalance.models import Holding, Portfolio


def portfolio(cash, *holdings):
    return Portfolio(D(str(cash)), {s: Holding(s, n, D(str(p))) for s, n, p in holdings})


def weights(**w):
    return {k: D(str(v)) for k, v in w.items()}
