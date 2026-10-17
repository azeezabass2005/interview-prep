from .game import FRAMES, PINS, Game


def symbols(game: Game) -> str:
    out = []
    for idx, (start, rolls) in enumerate(game.frames()[:FRAMES]):
        if idx == FRAMES - 1:
            tail = game.rolls[start:]
            marks, prev = [], None
            for pins in tail:
                if pins == PINS and (prev is None or prev == PINS or marks[-1] == "/"):
                    marks.append("X")
                elif prev is not None and prev != PINS and marks[-1] not in ("X", "/") and prev + pins == PINS:
                    marks.append("/")
                else:
                    marks.append("-" if pins == 0 else str(pins))
                prev = pins
            out.append("".join(marks))
            continue
        if rolls == [PINS]:
            out.append("X")
        elif len(rolls) == 2 and sum(rolls) == PINS:
            out.append(("-" if rolls[0] == 0 else str(rolls[0])) + "/")
        else:
            out.append("".join("-" if p == 0 else str(p) for p in rolls))
    return "|".join(out)
