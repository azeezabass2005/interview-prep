class GradebookError(Exception):
    status = 400


class NotFound(GradebookError):
    status = 404
