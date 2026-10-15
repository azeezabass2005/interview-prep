class LedgerError(Exception):
    status = 400


class InvalidAmount(LedgerError):
    status = 400


class InsufficientFunds(LedgerError):
    status = 409


class AccountNotOpen(LedgerError):
    status = 409


class NotFound(LedgerError):
    status = 404
