import itertools
from collections import defaultdict
from typing import Dict, List, Tuple

from .models import Layer, Shipment


class InMemoryStore:
    def __init__(self):
        self.layers: Dict[Tuple[str, str], List[Layer]] = defaultdict(list)
        self.shipments: Dict[str, Shipment] = {}
        self._seq = itertools.count(1)

    def add_layer(self, sku, warehouse, qty, unit_cost, received_on) -> Layer:
        layer = Layer(sku, warehouse, qty, unit_cost, received_on, next(self._seq))
        self.layers[(sku, warehouse)].append(layer)
        return layer

    def layers_for(self, sku: str, warehouse: str) -> List[Layer]:
        return [l for l in self.layers[(sku, warehouse)] if l.qty > 0]

    def on_hand(self, sku: str, warehouse: str) -> int:
        return sum(l.qty for l in self.layers_for(sku, warehouse))
