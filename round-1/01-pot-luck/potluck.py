import random
from decimal import ROUND_HALF_UP, Decimal

SPONSOR = Decimal("10000")
ENTRY_PRICE = Decimal("5")
MAX_ENTRIES = 10
TIERS = [(5, Decimal("1.00")), (4, Decimal("0.40")), (3, Decimal("0.20")), (2, Decimal("0.05"))]
CENT = Decimal("0.01")


class PotLuckError(Exception):
    pass


class Entry:
    def __init__(self, entry_id, participant, code):
        self.entry_id = entry_id
        self.participant = participant
        self.code = code
        self.active = True


class Draw:
    def __init__(self, number, rollover):
        self.number = number
        self.status = "OPEN"
        self.rollover_in = rollover
        self.winning_code = None
        self.pot = None
        self.entries = []


class PotLuck:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.participants = {}
        self.entries = {}
        self.draws = []
        self.rollover = Decimal("0")

    def register(self, participant_id, email):
        email = email.strip().lower()
        if email in self.participants.values():
            raise PotLuckError("email already registered")
        self.participants[participant_id] = email

    @property
    def current(self):
        return self.draws[-1] if self.draws else None

    def open_draw(self):
        if self.current is not None and self.current.status != "SETTLED":
            raise PotLuckError("previous draw is not settled")
        draw = Draw(len(self.draws) + 1, self.rollover)
        self.rollover = Decimal("0")
        self.draws.append(draw)
        return draw.number

    def _new_code(self):
        return str(self.rng.randint(0, 99999))

    def _open(self):
        draw = self.current
        if draw is None or draw.status != "OPEN":
            raise PotLuckError("no open draw")
        return draw

    def buy(self, participant_id, count=1):
        draw = self._open()
        if participant_id not in self.participants:
            raise PotLuckError("unknown participant")
        held = sum(1 for e in draw.entries if e.participant == participant_id)
        if held + count > MAX_ENTRIES:
            raise PotLuckError("entry limit reached")
        ids = []
        for _ in range(count):
            entry = Entry(len(self.entries) + 1, participant_id, self._new_code())
            self.entries[entry.entry_id] = entry
            draw.entries.append(entry)
            ids.append(entry.entry_id)
        return ids

    def cancel(self, entry_id):
        draw = self._open()
        entry = self.entries.get(entry_id)
        if entry is None or not entry.active or entry not in draw.entries:
            raise PotLuckError("no such active entry in the open draw")
        entry.active = False
        return ENTRY_PRICE

    def close(self):
        draw = self._open()
        active = [e for e in draw.entries if e.active]
        draw.pot = SPONSOR + ENTRY_PRICE * len(active) + draw.rollover_in
        draw.winning_code = self._new_code()
        draw.status = "CLOSED"
        return draw.winning_code

    @staticmethod
    def matches(code, winning):
        return len(set(code) & set(winning))

    def settle(self):
        draw = self.current
        if draw is None or draw.status != "CLOSED":
            raise PotLuckError("draw is not closed")
        by_tier = {}
        for entry in draw.entries:
            if entry.active:
                by_tier.setdefault(self.matches(entry.code, draw.winning_code), []).append(entry)
        remaining = draw.pot
        payouts = {}
        for matches, share in TIERS:
            winners = by_tier.get(matches)
            if not winners:
                continue
            amount = draw.pot * share
            each = (amount / len(winners)).quantize(CENT, rounding=ROUND_HALF_UP)
            for entry in winners:
                payouts[entry.entry_id] = each
            remaining -= each * len(winners)
        draw.status = "SETTLED"
        self.rollover = remaining
        return {"payouts": payouts, "rollover": remaining}
