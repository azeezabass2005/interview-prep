class CardError(Exception):
    status = 400


class NotFound(CardError):
    status = 404
