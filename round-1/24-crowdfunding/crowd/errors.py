class CrowdError(Exception):
    status = 400


class Rejected(CrowdError):
    status = 409


class NotFound(CrowdError):
    status = 404
