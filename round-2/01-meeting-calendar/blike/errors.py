class DomainError(Exception):
    pass


class ValidationError(DomainError):
    pass


class NotFound(DomainError):
    pass
