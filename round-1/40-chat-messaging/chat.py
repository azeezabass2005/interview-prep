import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Set

EDIT_WINDOW = timedelta(minutes=15)
MAX_PAGE = 100
MENTION = re.compile(r"@([a-z0-9_]+)")


class ChatError(Exception):
    pass


@dataclass
class Message:
    channel: str
    seq: int
    author: str
    text: str
    posted_at: datetime
    client_id: str


@dataclass
class Channel:
    name: str
    members: Set[str] = field(default_factory=set)
    messages: List[Message] = field(default_factory=list)
    last_read: Dict[str, int] = field(default_factory=dict)


class Chat:
    def __init__(self):
        self.channels = {}
        self.notifications = []
        self._seq = 0

    def create_channel(self, name, members):
        self.channels[name] = Channel(name, set(members))

    def _channel(self, name):
        if name not in self.channels:
            raise ChatError("no such channel")
        return self.channels[name]

    def post(self, channel, author, text, client_id, at):
        c = self._channel(channel)
        if author not in c.members:
            raise ChatError("not a member")
        for m in c.messages:
            if m.author == author and m.client_id == client_id:
                return m
        self._seq += 1
        message = Message(channel, self._seq, author, text, at, client_id)
        c.messages.append(message)
        for name in dict.fromkeys(MENTION.findall(text)):
            if name != author:
                self.notifications.append((name, channel, message.seq))
        return message

    def _message(self, channel, seq):
        for m in self._channel(channel).messages:
            if m.seq == seq:
                return m
        raise ChatError("no such message")

    def edit(self, channel, seq, author, text, at):
        m = self._message(channel, seq)
        if at - m.posted_at > EDIT_WINDOW:
            raise ChatError("edit window closed")
        m.text = text
        return m

    def delete(self, channel, seq, author):
        m = self._message(channel, seq)
        if m.author != author:
            raise ChatError("not your message")
        m.text = "[deleted]"

    def mark_read(self, channel, member, seq):
        c = self._channel(channel)
        c.last_read[member] = max(c.last_read.get(member, 0), seq)

    def unread(self, channel, member):
        c = self._channel(channel)
        last = c.last_read.get(member, 0)
        return sum(1 for m in c.messages if m.seq > last)

    def history(self, channel, before=None, limit=50):
        c = self._channel(channel)
        limit = min(limit, MAX_PAGE)
        older = [m for m in c.messages if before is None or m.seq <= before]
        return list(reversed(older))[:limit]
