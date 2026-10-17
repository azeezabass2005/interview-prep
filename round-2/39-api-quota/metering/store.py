from typing import Dict, Optional

from .models import Client


class InMemoryStore:
    def __init__(self):
        self.clients: Dict[str, Client] = {}

    def client(self, client_id: str) -> Optional[Client]:
        return self.clients.get(client_id)
