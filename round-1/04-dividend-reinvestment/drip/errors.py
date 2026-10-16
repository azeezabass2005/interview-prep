class DripError(Exception):
    status = 400


class NotFound(DripError):
    status = 404


class ValidationError(DripError):
    status = 400
