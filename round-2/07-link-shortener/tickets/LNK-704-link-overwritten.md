# LNK-704: A short link started pointing to a different page

**Type:** Bug · **Reporter:** Client services · **Priority:** Critical

## Description
A link we sent to clients months ago (`bbg.link/k3x9q2`) suddenly redirects to an internal survey created yesterday by another team.
We think the random code generator produced the same code twice.

## Acceptance criteria
- Increase `CODE_LENGTH` from 6 to 10 so collisions become practically impossible.
- An existing link's target never changes when a new link is created.

## Out of scope
- Letting users edit link targets.
