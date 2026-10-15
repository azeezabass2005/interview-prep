class LinkError(Exception):
    status = 400


class AliasTaken(LinkError):
    status = 409


class NotFound(LinkError):
    status = 404


class Gone(LinkError):
    status = 410
