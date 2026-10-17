class ExchangeError(Exception):
    status = 400


class Rejected(ExchangeError):
    status = 400


class NotFound(ExchangeError):
    status = 404
