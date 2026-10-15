from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Layer:
    sku: str
    qty: int
    unit_cost: Decimal
    received_on: date


@dataclass
class Shipment:
    shipment_id: str
    sku: str
    qty: int
    cogs: Decimal
    returned: int = 0


class InsufficientStock(Exception):
    pass
