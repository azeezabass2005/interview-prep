class PayrollError(Exception):
    status = 400


class NotFound(PayrollError):
    status = 404
