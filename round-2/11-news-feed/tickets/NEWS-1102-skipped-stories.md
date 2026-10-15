# NEWS-1102: Paging through the feed skips stories during busy news

**Type:** Bug · **Reporter:** Terminal news panel team · **Priority:** High

## Description
During busy periods users paging through the feed miss stories, and sometimes see the same story twice on consecutive pages.
Quiet periods are fine.

## Steps to reproduce
1. Feed has stories S1…S10 (newest first). User loads page 1 (limit 4): S10, S9, S8, S7.
2. Two new stories arrive (S11, S12).
3. User loads page 2 with the cursor from page 1: gets S8, S7, S6, S5 (repeats S8, S7; later pages skip others).

## Acceptance criteria
- Paging with the returned cursor continues exactly after the last story seen, regardless of new arrivals.

## Out of scope
- Showing a "new stories" banner.
