# R2-10 · Team Chat: interviewer notes

~390 lines. Theme: **which value is authoritative?** The server `seq`, not the device clock; the furthest read position, not the latest
request; the store's uniqueness, not a lookup.

## Ticket map

| Ticket | Real root cause | Where | Trap |
|---|---|---|---|
| MSG-1001 out of order | `recent()` orders by `client_sent_at` (device clock) | `repositories/messages.py::recent` | Using `received_at` (server time). Better than client time, but two instances' clocks can disagree and ties are common. `seq` is the documented order |
| MSG-1002 duplicates | Check-then-insert on `client_msg_id`; the index on (conversation, sender, client_msg_id) is **not UNIQUE** | `services/messaging.py::send`, `db.py` | Same as the workshop's calendar ticket. A process lock or second lookup doesn't hold across instances. Also: the loser has already burned a `seq` number (a gap). Discuss whether gaps matter (they don't for ordering; clients mustn't assume contiguity) |
| MSG-1003 unread badge | `set_last_read` overwrites with whatever the device sends; a stale device moves it **backwards** | `repositories/members.py::set_last_read` | **AC prescribes "only accept the most recently active device"**: complex, needs device tracking, and still wrong (a recently active device can be stale). The invariant "read position only moves forward" → `last_read_seq = MAX(last_read_seq, ?)` |
| MSG-1004 scroll-back | `before()` uses `ORDER BY seq ASC LIMIT n`, which picks the **oldest** n below the cursor | `repositories/messages.py::before` | Off-by-one at the boundary (must exclude `seq = before`) |

## MSG-1002 in depth
**Invariant:** at most one message per (conversation, sender, client_msg_id).
Accept: `UNIQUE` on those columns + catch `IntegrityError` → return the existing message. Even better: allocate `seq` and insert in **one**
transaction so a losing insert doesn't consume a sequence number. Keep the fast lookup.
Deterministic test: two `MessagingService` instances; pause the first two `find_by_client_id` calls on `Barrier(2)`.

## MSG-1003
One-line fix in SQL: `UPDATE members SET last_read_seq = MAX(last_read_seq, ?) …`. Atomic and order-independent. Ask: "Why is MAX better
than reading, comparing in Python, then writing?" (Because that's a check-then-act race between two devices.)

## Out-of-scope smells
- `mark_read` accepts a `seq` larger than the conversation's `last_seq` (unread would go weird). Mention it.
- Moderation masks words, but the original text is never stored (a product decision).

## Strong prompts
- "Which fields could be used to order messages? For each, who sets it and can it go backwards? Don't change code."
- "If two devices call mark-read with 5 and then 3, what's stored? Show the line."
