class MeteringError(Exception):
    status = 400


class NotFound(MeteringError):
    status = 404
