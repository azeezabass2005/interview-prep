from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Layer:
    sku: str
    warehouse: str
    qty: int
    unit_cost: Decimal
    received_on: date
    seq: int


@dataclass
class Shipment:
    shipment_id: str
    sku: str
    warehouse: str
    qty: int
    cogs: Decimal
    returned: int = 0
