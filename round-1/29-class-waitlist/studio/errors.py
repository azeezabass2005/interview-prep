class StudioError(Exception):
    status = 400


class Refused(StudioError):
    status = 409


class NotFound(StudioError):
    status = 404
