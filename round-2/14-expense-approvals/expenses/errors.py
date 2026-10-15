class ExpenseError(Exception):
    status = 400


class NotAllowed(ExpenseError):
    status = 403


class InvalidState(ExpenseError):
    status = 409


class NotFound(ExpenseError):
    status = 404
