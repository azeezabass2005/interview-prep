class GarageError(Exception):
    status = 400


class GarageFull(GarageError):
    status = 409


class NotFound(GarageError):
    status = 404


class InvalidState(GarageError):
    status = 409
