class DocError(Exception):
    status = 400


class NotFound(DocError):
    status = 404


class VersionConflict(DocError):
    status = 409
