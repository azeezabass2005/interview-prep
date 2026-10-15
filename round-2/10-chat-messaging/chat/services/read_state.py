from ..db import Database
from ..errors import NotMember
from ..repositories.conversations import ConversationRepository
from ..repositories.members import MemberRepository
from ..repositories.messages import MessageRepository


class ReadStateService:
    def __init__(self, db: Database):
        self._members = MemberRepository(db)
        self._messages = MessageRepository(db)
        self._conversations = ConversationRepository(db)

    def mark_read(self, conversation_id: str, user_id: str, seq: int) -> None:
        if not self._conversations.is_member(conversation_id, user_id):
            raise NotMember(user_id)
        self._members.set_last_read(conversation_id, user_id, seq)

    def unread(self, conversation_id: str, user_id: str) -> int:
        return self._messages.count_unread(conversation_id, user_id, self._members.last_read(conversation_id, user_id))
