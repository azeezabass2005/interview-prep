class TourneyError(Exception):
    status = 400


class Rejected(TourneyError):
    status = 409


class NotFound(TourneyError):
    status = 404
