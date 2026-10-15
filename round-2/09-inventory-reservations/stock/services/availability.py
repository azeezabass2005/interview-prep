from ..errors import NotFound
from ..repositories.skus import SkuRepository


class AvailabilityService:
    def __init__(self, skus: SkuRepository):
        self._skus = skus

    def available(self, sku: str) -> int:
        item = self._skus.get(sku)
        if item is None:
            raise NotFound(sku)
        if not item.is_bundle:
            return item.available
        components = self._skus.components(sku)
        return min(self._skus.get(component).available for component in components)
