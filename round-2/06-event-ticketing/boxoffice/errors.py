class BoxOfficeError(Exception):
    status = 400


class SeatUnavailable(BoxOfficeError):
    status = 409


class RefundNotAllowed(BoxOfficeError):
    status = 409


class NotFound(BoxOfficeError):
    status = 404
