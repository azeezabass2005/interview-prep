import uuid
from datetime import datetime
from typing import List

from ..config import DEFAULT_PAGE, MAX_BODY_LENGTH, MAX_PAGE
from ..db import Database
from ..errors import ChatError, NotMember
from ..models import Message
from ..repositories.conversations import ConversationRepository
from ..repositories.messages import MessageRepository
from .moderation import mask


class MessagingService:
    def __init__(self, db: Database, clock):
        self._conversations = ConversationRepository(db)
        self._messages = MessageRepository(db)
        self._clock = clock

    def _require_member(self, conversation_id: str, user_id: str) -> None:
        if not self._conversations.is_member(conversation_id, user_id):
            raise NotMember(f"{user_id} is not in {conversation_id}")

    def send(self, conversation_id: str, sender: str, client_msg_id: str, body: str,
             client_sent_at: datetime) -> Message:
        self._require_member(conversation_id, sender)
        if not body or len(body) > MAX_BODY_LENGTH:
            raise ChatError("message body must be 1-4000 characters")
        existing = self._messages.find_by_client_id(conversation_id, sender, client_msg_id)
        if existing is not None:
            return existing
        seq = self._conversations.next_seq(conversation_id)
        message = Message(f"msg_{uuid.uuid4().hex[:12]}", conversation_id, seq, sender, mask(body), client_msg_id,
                          client_sent_at, self._clock.now())
        self._messages.insert(message)
        return message

    def recent(self, conversation_id: str, user_id: str, limit: int = DEFAULT_PAGE) -> List[Message]:
        self._require_member(conversation_id, user_id)
        return self._messages.recent(conversation_id, min(limit, MAX_PAGE))

    def before(self, conversation_id: str, user_id: str, before_seq: int, limit: int = DEFAULT_PAGE) -> List[Message]:
        self._require_member(conversation_id, user_id)
        return self._messages.before(conversation_id, before_seq, min(limit, MAX_PAGE))
