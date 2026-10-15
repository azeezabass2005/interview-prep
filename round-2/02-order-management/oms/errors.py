class OmsError(Exception):
    status = 400


class ValidationError(OmsError):
    status = 400


class NotFound(OmsError):
    status = 404


class InvalidState(OmsError):
    status = 409
