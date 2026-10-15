class RoomError(Exception):
    status = 400


class Conflict(RoomError):
    status = 409


class NotFound(RoomError):
    status = 404
