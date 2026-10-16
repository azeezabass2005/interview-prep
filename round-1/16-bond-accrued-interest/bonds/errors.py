class BondError(Exception):
    status = 400


class NotFound(BondError):
    status = 404
