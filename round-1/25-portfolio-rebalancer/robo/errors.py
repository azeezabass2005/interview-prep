class RoboError(Exception):
    status = 400


class NotFound(RoboError):
    status = 404
