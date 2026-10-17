# League Standings

A federation publishes standings for an amateur football league. Fixtures are scheduled before the season; referees enter results after
each match (and occasionally **correct** a result entered by mistake). The repository contains the standings service.

## Results

- A result belongs to a scheduled fixture. Entering a result for a fixture that already has one **replaces** it.
- Postponed fixtures (no result) don't count.
- **Points:** win 3, draw 1, loss 0. **Deductions** (penalties) are subtracted from a team's points.

## Ordering

1. points (high to low)
2. goal difference (scored − conceded)
3. goals scored
4. **head-to-head points** counting **only matches between the teams still tied**
5. team name, alphabetically (display only)

Teams still level after step 4 **share a position**; the next team's position skips (1, 2, 2, 4).

## Form guide

The last 5 results per team, oldest first, as W/D/L, by fixture date.

## Example

Results: Zeta 1–0 Alpha · Cobras 1–0 Zeta · Alpha 1–0 Dynamo.

| Pos | Team | Pts | GD | GF |
|---|---|---|---|---|
| 1 | Cobras | 3 | +1 | 1 |
| 2 | Zeta | 3 | 0 | 1 |
| 3 | Alpha | 3 | 0 | 1 |
| 4 | Dynamo | 0 | −1 | 0 |

Zeta ranks above Alpha on head-to-head.
