# LB-1903: Tied participants appear in random order across pages

**Type:** Bug · **Reporter:** Web app team · **Priority:** Medium

## Description
At the start of each week most participants have the same score. Pages list tied participants in an arbitrary order (it looks like newest
sign-ups first), not alphabetically as the rules say. After a database maintenance window, users reported seeing the same name on two pages
and someone missing.

## Acceptance criteria
- Within a tie, participants are listed alphabetically by name, on every page.
- Paging through the whole board shows every participant exactly once.

## Out of scope
- Infinite scroll.
