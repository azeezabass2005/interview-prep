from dataclasses import dataclass


@dataclass
class Instrument:
    symbol: str
    name: str
    exchange: str
    currency: str
    kind: str


@dataclass
class Quote:
    symbol: str
    price: float
    currency: str
    as_of: str
    source: str = "tickstream"


@dataclass
class Bar:
    day: str
    open: float
    high: float
    low: float
    close: float
    volume: int
