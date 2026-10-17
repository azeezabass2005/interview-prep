class InventoryError(Exception):
    status = 400


class InsufficientStock(InventoryError):
    status = 409


class NotFound(InventoryError):
    status = 404
