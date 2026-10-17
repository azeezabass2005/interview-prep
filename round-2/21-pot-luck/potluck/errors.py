class PotLuckError(Exception):
    status = 400


class ValidationError(PotLuckError):
    status = 400


class NotFound(PotLuckError):
    status = 404


class InvalidState(PotLuckError):
    status = 409


class LimitExceeded(PotLuckError):
    status = 422
