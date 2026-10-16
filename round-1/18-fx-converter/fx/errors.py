class FxError(Exception):
    status = 400


class NotFound(FxError):
    status = 404


class Rejected(FxError):
    status = 409
