class AuctionError(Exception):
    status = 400


class Rejected(AuctionError):
    status = 409


class NotFound(AuctionError):
    status = 404
