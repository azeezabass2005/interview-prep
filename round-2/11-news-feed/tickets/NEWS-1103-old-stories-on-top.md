# NEWS-1103: Day-old stories outrank breaking news

**Type:** Bug · **Reporter:** News desk · **Priority:** Medium

## Description
In the "Top" view, yesterday's stories from high-weight sources sit above stories published minutes ago. A 24-hour-old story should be
worth 1/16 of a fresh one from the same source.

## Acceptance criteria
- Scores halve every 6 hours of age, as documented.

## Out of scope
- Changing source weights.
