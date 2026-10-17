class IpoError(Exception):
    status = 400


class InvalidState(IpoError):
    status = 409


class NotFound(IpoError):
    status = 404
