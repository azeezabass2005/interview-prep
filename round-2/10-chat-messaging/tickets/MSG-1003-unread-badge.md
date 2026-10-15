# MSG-1003: Unread badge comes back after reading on another device

**Type:** Bug · **Reporter:** Desktop team · **Priority:** Medium

## Description
A user reads a conversation on their phone (badge clears), then opens their laptop, which was offline. The laptop syncs its older read
position and the unread badge reappears on every device, showing messages the user already read.

## Steps to reproduce
1. Conversation with 5 messages from others.
2. Phone marks read up to seq 5 → unread 0.
3. Laptop (stale) marks read up to seq 3 → unread is 2 again.

## Acceptance criteria
- Only accept mark-read requests from the user's most recently active device.
- Reading on one device clears the badge everywhere and it doesn't come back.

## Out of scope
- Per-device read receipts.
