from collections import defaultdict
from typing import Dict, List, Tuple

from .models import Payment, Quote


class InMemoryStore:
    def __init__(self):
        self.rates: Dict[str, Tuple] = {}
        self.quotes: Dict[str, Quote] = {}
        self.payments: Dict[str, Payment] = {}
        self.payments_by_customer: Dict[str, List[str]] = defaultdict(list)
