import random

from .config import CODE_LENGTH, ENTRY_FEE_CENTS, SPONSOR_SEED_CENTS
from .models import Draw, Entry, PayoutPlan
from .payouts import build_payout_plan


class PotLuck:
    """Runs a sequence of draws. Each draw: accept entries -> close -> settle."""

    def __init__(self, rng=None):
        self._rng = rng or random.Random()
        self._entries = []
        self._next_entry_id = 1
        self._draw_number = 1
        self._rollover_cents = 0
        self._closed = False

    @property
    def draw_number(self):
        return self._draw_number

    def add_entry(self, participant: str) -> Entry:
        if not participant:
            raise ValueError("participant is required")
        entry = Entry(self._next_entry_id, participant, self._generate_code())
        self._next_entry_id += 1
        self._entries.append(entry)
        return entry

    def current_pot_cents(self) -> int:
        return SPONSOR_SEED_CENTS + ENTRY_FEE_CENTS * len(self._entries)

    def close(self) -> Draw:
        """Generate the winning code and freeze the draw."""
        if self._closed:
            raise RuntimeError("draw already closed")
        self._closed = True
        winning_code = self._generate_code()
        return Draw(
            draw_number=self._draw_number,
            winning_code=winning_code,
            pot_cents=self.current_pot_cents(),
            entries=self._entries,
        )

    def settle(self, draw: Draw) -> PayoutPlan:
        plan = build_payout_plan(draw)
        self._rollover_cents = plan.rollover_cents
        return plan

    def start_next_draw(self):
        self._entries.clear()
        self._draw_number += 1
        self._closed = False

    def _generate_code(self) -> str:
        return str(self._rng.randint(0, 10 ** CODE_LENGTH - 1))
