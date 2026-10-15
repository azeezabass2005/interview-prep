from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Message:
    message_id: str
    conversation_id: str
    seq: int
    sender: str
    body: str
    client_msg_id: str
    client_sent_at: datetime
    received_at: datetime
