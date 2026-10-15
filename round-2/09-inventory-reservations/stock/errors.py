class StockError(Exception):
    status = 400


class InsufficientStock(StockError):
    status = 409


class NotFound(StockError):
    status = 404
