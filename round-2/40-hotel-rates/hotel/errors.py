class HotelError(Exception):
    status = 400


class Unavailable(HotelError):
    status = 409


class NotFound(HotelError):
    status = 404
