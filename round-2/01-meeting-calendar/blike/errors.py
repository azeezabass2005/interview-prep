class DomainError(Exception):
    """Base class for errors the API turns into 4xx responses."""


class ValidationError(DomainError):
    pass


class NotFound(DomainError):
    pass
