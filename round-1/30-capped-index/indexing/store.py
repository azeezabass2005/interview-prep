from typing import Dict

from .models import IndexDefinition, Security


class InMemoryStore:
    def __init__(self):
        self.universe: Dict[str, Security] = {}
        self.indices: Dict[str, IndexDefinition] = {}
