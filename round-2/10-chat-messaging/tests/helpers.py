import os
import tempfile
from datetime import datetime, timedelta

from chat.api.handlers import ChatApi
from chat.clock import FakeClock
from chat.db import Database
from chat.repositories.conversations import ConversationRepository
from chat.repositories.messages import MessageRepository
from chat.services.messaging import MessagingService
from chat.services.read_state import ReadStateService

T0 = datetime(2026, 4, 2, 12, 0, 0)


class World:
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()
        self.db = Database(os.path.join(self._dir.name, "chat.db"))
        self.db.initialize()
        self.clock = FakeClock(T0)
        ConversationRepository(self.db).create("lunch", "Lunch crew", ["ann", "bob", "cy"])
        self.messaging = MessagingService(self.db, self.clock)
        self.api = ChatApi(self.messaging, ReadStateService(self.db))
        self.messages = MessageRepository(self.db)

    def send(self, user, text, client_id=None, client_offset_s=0):
        self.clock.advance(1)
        sent_at = (self.clock.now() + timedelta(seconds=client_offset_s)).isoformat()
        return self.api.post_message(user, "lunch", {"client_msg_id": client_id or f"{user}-{text}",
                                                     "body": text, "client_sent_at": sent_at})

    def cleanup(self):
        self._dir.cleanup()
