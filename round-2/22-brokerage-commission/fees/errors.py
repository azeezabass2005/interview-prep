class FeeError(Exception):
    status = 400


class ValidationError(FeeError):
    status = 400


class NotFound(FeeError):
    status = 404


class InvalidState(FeeError):
    status = 409
