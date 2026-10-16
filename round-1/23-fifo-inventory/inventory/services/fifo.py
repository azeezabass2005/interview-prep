from decimal import Decimal
from typing import List, Tuple

from ..models import Layer
from ..store import InMemoryStore


def take(store: InMemoryStore, sku: str, warehouse: str, qty: int) -> List[Tuple[Layer, int]]:
    taken = []
    remaining = qty
    for layer in sorted(store.layers_for(sku, warehouse), key=lambda l: (l.received_on, l.seq), reverse=True):
        if remaining == 0:
            break
        n = min(layer.qty, remaining)
        taken.append((layer, n))
        remaining -= n
        layer.qty = layer.qty - n if n == layer.qty else n
    return taken


def cost_of(taken) -> Decimal:
    return sum((layer.unit_cost * n for layer, n in taken), Decimal("0"))
