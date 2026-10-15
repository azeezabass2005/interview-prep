MINOR_UNITS = {
    "USD": 2,
    "EUR": 2,
    "GBP": 2,
    "CHF": 2,
    "KWD": 3,
}


def minor_units(currency: str) -> int:
    return MINOR_UNITS.get(currency, 2)
