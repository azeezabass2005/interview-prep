class MarginError(Exception):
    status = 400


class NotFound(MarginError):
    status = 404
