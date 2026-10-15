from typing import List

from ..repositories.skus import SkuRepository


def low_stock(skus: SkuRepository) -> List[dict]:
    return [{"sku": s.sku, "name": s.name, "on_hand": s.on_hand, "reorder_point": s.reorder_point}
            for s in skus.all_stocked() if s.on_hand < s.reorder_point]
