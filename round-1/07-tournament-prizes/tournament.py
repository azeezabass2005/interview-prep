from decimal import ROUND_DOWN, Decimal

BUY_IN = Decimal("100")
TO_POOL = Decimal("85")
MAX_REENTRIES = 2
PAYOUTS = [(2, [65, 35]), (10, [50, 30, 20]), (30, [40, 25, 15, 10, 10])]
DOLLAR = Decimal("1")


class TournamentError(Exception):
    pass


class Tournament:
    def __init__(self, guarantee=0):
        self.guarantee = Decimal(str(guarantee))
        self.registration_open = True
        self.entries = []
        self.active = set()
        self.busted = set()
        self.finish = {}

    @property
    def players(self):
        return set(self.entries)

    def register(self, player):
        if not self.registration_open:
            raise TournamentError("registration is closed")
        if player in self.active:
            raise TournamentError("player is still in")
        if self.entries.count(player) > 1 + MAX_REENTRIES:
            raise TournamentError("no re-entries left")
        self.entries.append(player)
        self.active.add(player)
        self.busted.discard(player)

    def close_registration(self):
        self.registration_open = False

    def eliminate(self, chips):
        for player in chips:
            if player not in self.active:
                raise TournamentError(f"{player} is not in the tournament")
        if self.registration_open:
            for player in chips:
                self.active.remove(player)
                self.busted.add(player)
            return {}
        position = len(self.active)
        placed = {}
        for player in sorted(chips, key=lambda p: chips[p], reverse=True):
            placed[player] = position
            position -= 1
            self.active.remove(player)
        if len(self.active) == 1:
            placed[next(iter(self.active))] = 1
        self.finish.update(placed)
        return placed

    def prize_pool(self):
        return max(TO_POOL * len(self.players), self.guarantee)

    def _percentages(self):
        count = len(self.entries)
        chosen = []
        for minimum, table in PAYOUTS:
            if count > minimum:
                chosen = table
        return chosen

    def prizes(self):
        pool = self.prize_pool()
        amounts = [(pool * pct / 100).quantize(DOLLAR, rounding=ROUND_DOWN) for pct in self._percentages()]
        if amounts:
            amounts[-1] += pool - sum(amounts)
        return {place + 1: amount for place, amount in enumerate(amounts)}

    def results(self):
        prizes = self.prizes()
        return {player: (pos, prizes.get(pos, Decimal("0"))) for player, pos in self.finish.items()}
