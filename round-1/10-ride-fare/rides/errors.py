class RideError(Exception):
    status = 400


class InvalidState(RideError):
    status = 409


class NotFound(RideError):
    status = 404
