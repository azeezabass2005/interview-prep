class AlertsError(Exception):
    status = 400


class ValidationError(AlertsError):
    status = 400


class NotFound(AlertsError):
    status = 404
