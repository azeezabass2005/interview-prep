from decimal import ROUND_HALF_UP, Decimal

from ..store import InMemoryStore


def valuation(store: InMemoryStore, sku: str, warehouse: str) -> Decimal:
    total = sum((l.qty * l.unit_cost for l in store.layers_for(sku, warehouse)), Decimal("0"))
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def all_valuations(store: InMemoryStore) -> dict:
    return {f"{sku}@{wh}": str(valuation(store, sku, wh)) for (sku, wh) in sorted(store.layers)}
