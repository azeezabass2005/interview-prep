class QueueError(Exception):
    status = 400


class NotFound(QueueError):
    status = 404


class LeaseLost(QueueError):
    status = 409
