class TabError(Exception):
    status = 400


class ValidationError(TabError):
    status = 400


class NotFound(TabError):
    status = 404
