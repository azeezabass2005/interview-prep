# MSG-1004: Scrolling up jumps to the start of the conversation

**Type:** Bug · **Reporter:** Desktop team · **Priority:** Medium

## Description
In long conversations, scrolling up loads the **first** messages ever sent instead of the ones just above what's on screen.

## Steps to reproduce
1. Conversation with 10 messages (seq 1–10). The screen shows seq 8–10.
2. Client calls `before=8&limit=3`.
3. Response contains seq 1, 2, 3. Expected 5, 6, 7.

## Acceptance criteria
- `before=S&limit=N` returns the N messages immediately before S, oldest first.

## Out of scope
- Forward pagination.
