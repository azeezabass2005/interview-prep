class LibraryError(Exception):
    status = 400


class Refused(LibraryError):
    status = 409


class NotFound(LibraryError):
    status = 404
