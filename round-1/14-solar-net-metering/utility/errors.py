class BillingError(Exception):
    status = 400


class NotFound(BillingError):
    status = 404
