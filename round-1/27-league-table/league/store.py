from typing import Dict, List

from .models import Fixture, Result


class InMemoryStore:
    def __init__(self):
        self.teams: List[str] = []
        self.fixtures: Dict[str, Fixture] = {}
        self.results: List[Result] = []
        self.deductions: Dict[str, int] = {}
