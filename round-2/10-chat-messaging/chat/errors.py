class ChatError(Exception):
    status = 400


class NotMember(ChatError):
    status = 403


class NotFound(ChatError):
    status = 404
