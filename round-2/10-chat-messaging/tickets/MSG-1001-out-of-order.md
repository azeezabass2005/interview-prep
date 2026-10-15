# MSG-1001: Messages appear out of order in group chats

**Type:** Bug · **Reporter:** Mobile team · **Priority:** High

## Description
In a group chat, Bob's replies sometimes show **above** the messages he was replying to. Bob's phone clock turned out to be 3 minutes
behind. Other users with wrong clocks cause the same thing.

## Steps to reproduce
1. Ann sends "lunch?" (her phone clock 12:00:00).
2. Bob replies "yes!" (his phone clock says 11:57:10).
3. `GET /conversations/{id}/messages` lists "yes!" before "lunch?".

## Acceptance criteria
- Messages are listed in the order the server accepted them.

## Out of scope
- Fixing device clocks.
