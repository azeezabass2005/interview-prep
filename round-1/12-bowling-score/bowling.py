from decimal import Decimal

FRAMES = 10
PINS = 10
HANDICAP_BASIS = 200
HANDICAP_PCT = Decimal("0.9")


class BowlingError(Exception):
    pass


def _validate(rolls):
    i, frame = 0, 1
    for pins in rolls:
        if not 0 <= pins <= PINS:
            raise BowlingError(f"bad roll {pins}")
    while frame < FRAMES and i < len(rolls):
        if rolls[i] == PINS:
            i += 1
        else:
            if i + 1 < len(rolls) and rolls[i] + rolls[i + 1] > PINS:
                raise BowlingError(f"frame {frame} has more than {PINS} pins")
            i += 2
        frame += 1


def _add(total, points, known):
    return total + points if total is not None and known else None


def frame_scores(rolls):
    _validate(rolls)
    scores, total, i, frame = [], 0, 0, 0
    while i < len(rolls):
        frame += 1
        if rolls[i] == PINS:
            bonus = rolls[i + 1:i + 3]
            total = _add(total, PINS + sum(bonus), True)
            i += 1
        elif i + 1 < len(rolls) and rolls[i] + rolls[i + 1] == PINS:
            bonus = rolls[i + 2:i + 4]
            total = _add(total, PINS + sum(bonus), len(bonus) > 0)
            i += 2
        elif i + 1 < len(rolls):
            total = _add(total, rolls[i] + rolls[i + 1], True)
            i += 2
        else:
            total = _add(total, rolls[i], False)
            i += 1
        scores.append(total)
    return scores


class League:
    def __init__(self):
        self.games = {}

    def average(self, bowler):
        games = self.games.get(bowler, [])
        return sum(games) // len(games) if games else None

    def handicap(self, bowler):
        average = self.average(bowler)
        if average is None:
            return 0
        return int((HANDICAP_BASIS - average) * HANDICAP_PCT)

    def _final(self, rolls):
        scores = frame_scores(rolls)
        if len(scores) < FRAMES or scores[-1] is None:
            raise BowlingError("game is not finished")
        return scores[-1]

    def match(self, a, rolls_a, b, rolls_b):
        scratch = {a: self._final(rolls_a), b: self._final(rolls_b)}
        for bowler, score in scratch.items():
            self.games.setdefault(bowler, []).append(score)
        result = {}
        for bowler in (a, b):
            hcp = self.handicap(bowler)
            result[bowler] = {"scratch": scratch[bowler], "handicap": hcp, "total": scratch[bowler] + hcp}
        ta, tb = result[a]["total"], result[b]["total"]
        result[a]["points"] = 2 if ta > tb else 1 if ta == tb else 0
        result[b]["points"] = 2 - result[a]["points"]
        return result
