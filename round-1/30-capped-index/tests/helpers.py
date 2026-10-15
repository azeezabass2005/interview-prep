from decimal import Decimal as D

from index.models import Security


def sec(ticker, relative_size, free_float="1.0", price="10"):
    """relative_size billions of dollars of float-adjusted cap when free_float is 1."""
    shares = int(relative_size * 100_000_000)
    return Security(ticker, shares, D(free_float), D(price))
