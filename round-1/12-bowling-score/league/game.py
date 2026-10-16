from typing import List, Optional, Tuple

from .errors import InvalidRoll

FRAMES = 10
PINS = 10


class Game:
    def __init__(self, rolls=()):
        self.rolls: List[int] = []
        for pins in rolls:
            self.roll(pins)

    def roll(self, pins: int) -> None:
        if not isinstance(pins, int) or not 0 <= pins <= PINS:
            raise InvalidRoll(f"invalid pin count {pins}")
        if self.is_complete():
            raise InvalidRoll("game is complete")
        self.rolls.append(pins)

    def frames(self) -> List[Tuple[int, List[int]]]:
        frames, i = [], 0
        while i < len(self.rolls):
            if self.rolls[i] == PINS:
                frames.append((i, [PINS]))
                i += 1
            else:
                frames.append((i, self.rolls[i:i + 2]))
                i += 2
        return frames

    def is_complete(self) -> bool:
        frames = self.frames()
        if len(frames) < FRAMES:
            return False
        start, tenth = frames[FRAMES - 1]
        bonus = tenth[0] == PINS or (len(tenth) == 2 and sum(tenth) == PINS)
        return len(self.rolls) - start >= (3 if bonus else 2)

    def frame_totals(self) -> List[Optional[int]]:
        frames = self.frames()
        totals, running = [], 0
        for idx, (start, rolls) in enumerate(frames):
            nxt = frames[idx + 1][1] if idx + 1 < len(frames) else []
            if rolls == [PINS]:
                bonus_rolls = nxt[:2]
                if len(bonus_rolls) < 2:
                    totals.append(None)
                    continue
                running += PINS + sum(bonus_rolls)
            elif len(rolls) == 2 and sum(rolls) == PINS:
                if not nxt:
                    totals.append(None)
                    continue
                running += PINS + nxt[0]
            elif len(rolls) == 2:
                running += sum(rolls)
            else:
                totals.append(None)
                continue
            totals.append(running)
        return totals

    def score(self) -> int:
        known = [t for t in self.frame_totals() if t is not None]
        return known[-1] if known else 0
