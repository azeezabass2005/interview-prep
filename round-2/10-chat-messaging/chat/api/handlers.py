from dataclasses import dataclass, field
from datetime import datetime

from ..errors import ChatError
from ..models import Message
from ..services.messaging import MessagingService
from ..services.read_state import ReadStateService


@dataclass
class Response:
    status: int
    body: dict = field(default_factory=dict)


def msg_json(m: Message) -> dict:
    return {"message_id": m.message_id, "seq": m.seq, "sender": m.sender, "body": m.body,
            "client_sent_at": m.client_sent_at.isoformat()}


class ChatApi:
    def __init__(self, messaging: MessagingService, reads: ReadStateService):
        self._messaging = messaging
        self._reads = reads

    def _run(self, fn):
        try:
            return fn()
        except ChatError as e:
            return Response(e.status, {"error": str(e)})

    def post_message(self, user: str, conversation_id: str, body: dict) -> Response:
        return self._run(lambda: Response(201, msg_json(self._messaging.send(
            conversation_id, user, body["client_msg_id"], body["body"], datetime.fromisoformat(body["client_sent_at"])))))

    def get_messages(self, user: str, conversation_id: str, before=None, limit=50) -> Response:
        def go():
            if before is None:
                msgs = self._messaging.recent(conversation_id, user, limit)
            else:
                msgs = self._messaging.before(conversation_id, user, int(before), limit)
            return Response(200, {"messages": [msg_json(m) for m in msgs]})
        return self._run(go)

    def post_read(self, user: str, conversation_id: str, body: dict) -> Response:
        def go():
            self._reads.mark_read(conversation_id, user, int(body["seq"]))
            return Response(200, {"unread": self._reads.unread(conversation_id, user)})
        return self._run(go)

    def get_unread(self, user: str, conversation_id: str) -> Response:
        return Response(200, {"unread": self._reads.unread(conversation_id, user)})
