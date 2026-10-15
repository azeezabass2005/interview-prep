FIXES = [
    ("bowling/game.py",
     """        frames = self._frames()
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
        return totals""",
     """        frames = self._frames()[:FRAMES]
        totals: List[Optional[int]] = []
        running = 0
        for start, rolls in frames:
            if rolls == [PINS]:
                needed = 3
            elif len(rolls) == 2 and sum(rolls) == PINS:
                needed = 3
            else:
                needed = 2
            window = self.rolls[start:start + needed]
            if len(window) < needed:
                totals.extend([None] * (len(frames) - len(totals)))
                break
            running += sum(window)
            totals.append(running)
        return totals"""),
    ("bowling/game.py",
     """            raise BowlingError(f"invalid pin count {pins}")
        self.rolls.append(pins)""",
     """            raise BowlingError(f"invalid pin count {pins}")
        if self.is_complete():
            raise BowlingError("game is over")
        frames = self._frames()
        if frames and len(frames) < FRAMES:
            _, last = frames[-1]
            if len(last) == 1 and last[0] != PINS and last[0] + pins > PINS:
                raise BowlingError("a frame cannot exceed 10 pins")
        self.rolls.append(pins)"""),
]
