class LoyaltyError(Exception):
    status = 400


class NotFound(LoyaltyError):
    status = 404


class InsufficientMiles(LoyaltyError):
    status = 409
