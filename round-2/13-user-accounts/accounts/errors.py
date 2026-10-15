class AccountsError(Exception):
    status = 400


class EmailTaken(AccountsError):
    status = 409


class InvalidCredentials(AccountsError):
    status = 401


class AccountLocked(AccountsError):
    status = 423


class InvalidToken(AccountsError):
    status = 400
