from typing import List, Optional, Tuple

FRAMES = 10
PINS = 10

Frame = Tuple[int, List[int]]  # (index of the frame's first roll, rolls in the frame)


class BowlingError(Exception):
    pass


class Game:
    def __init__(self):
        self.rolls: List[int] = []

    def roll(self, pins: int) -> None:
        if not 0 <= pins <= PINS:
            raise BowlingError(f"invalid pin count {pins}")
        self.rolls.append(pins)

    def _frames(self) -> List[Frame]:
        frames: List[Frame] = []
        i = 0
        while i < len(self.rolls):
            if self.rolls[i] == PINS:
                frames.append((i, [PINS]))
                i += 1
            else:
                frames.append((i, self.rolls[i:i + 2]))
                i += 2
        return frames

    def is_complete(self) -> bool:
        frames = self._frames()
        if len(frames) < FRAMES:
            return False
        start, tenth = frames[FRAMES - 1]
        earned_bonus = tenth[0] == PINS or (len(tenth) == 2 and sum(tenth) == PINS)
        needed = 3 if earned_bonus else 2
        return len(self.rolls) - start >= needed

    def frame_scores(self) -> List[Optional[int]]:
        frames = self._frames()
        totals: List[Optional[int]] = []
        running = 0
        for idx, (start, rolls) in enumerate(frames):
            points = sum(rolls)
            next_rolls = frames[idx + 1][1] if idx + 1 < len(frames) else []
            if rolls == [PINS]:
                points += sum(next_rolls[:2])
            elif len(rolls) == 2 and sum(rolls) == PINS:
                points += next_rolls[0] if next_rolls else 0
            running += points
            totals.append(running)
        return totals

    def score(self) -> int:
        totals = [t for t in self.frame_scores() if t is not None]
        return totals[-1] if totals else 0
