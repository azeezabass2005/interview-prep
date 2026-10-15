from decimal import Decimal as D

from margin.models import Account, Position


def example_account(cash="-100000"):
    return Account("ACC1", D(cash), [
        Position("AAPL", "EQUITY", 400, D("200")),
        Position("TLT", "BOND", 300, D("100")),
        Position("SPY", "ETF", 50, D("400")),
    ])
