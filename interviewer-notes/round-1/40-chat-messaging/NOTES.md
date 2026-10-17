# R1-40 · Chat Messaging: Interviewer Guide

The Round 1 version of Round 2 #10. One file, `chat.py` (~95 lines), with one passing test. **The spec example fails on the buggy
code** (B2: Ana's unread count is 2 because her own message counts).

## Session plan (60 min)
0–5 resume · 5–12 spec summary + questions · 12–17 code walk · 17–45 bug hunt · 45–55 DS questions + feature request · 55–60 risks.

## PM answers
| Question | Answer |
|---|---|
| Edit at exactly 15 minutes | Allowed. |
| Mentioning yourself | No notification. |
| Same client id in two channels | Two messages (scope is channel + author). |
| `before=1` | Empty page. |
| Deleted message in unread count | Still counts. |

## Code map
`create_channel` · `post` (membership, dedupe, seq, mentions) · `edit` · `delete` · `mark_read` · `unread` · `history`.

## Planted bugs (5)

### B1 · Global sequence numbers
- **Where:** `post`: `self._seq`.
- **Test:** first message in a second channel → **seq 1**.

### B2 · Own messages counted as unread
- **Where:** `unread`.
- **Test:** the spec example; or Ana 2, Ben 1 → Ana's unread **1**.

### B3 · Anyone can edit
- **Where:** `edit` takes `author` and never checks it (clue: `delete` does).
- **Test:** Ben edits Ana's message → refused.

### B4 · `before` is inclusive
- **Where:** `history`: `m.seq <= before`.
- **Test:** 5 messages, `before=3, limit=2` → **[2, 1]** (buggy [3, 2]: page overlap).

### B5 · Non-members get mention notifications
- **Where:** `post`.
- **Test:** "@zed and @ben" where Zed isn't a member → only **ben** notified.

Hints: (1) "compare `edit` and `delete`"; (2) "page through 5 messages two at a time".

## Red herrings
- `mark_read` never moves backwards (`max`): correct.
- Dedupe by (author, client id) within the channel: correct.

## Questions about the candidate's fixes (data structures)
- **Messages as a list per channel:** "`_message` scans: O(n). Since seq = index + 1, what's O(1)?" (`messages[seq - 1]` — only if messages are never removed; deletion is soft, so it holds.)
- **`history`:** "Building `older` copies the whole list each page: O(n). Better?" (Slice by index: `messages[max(0, before-1-limit):before-1]` reversed: O(limit).)
- **Unread counts for 10,000 channels:** "Computing on demand is O(messages). Alternative?" (Unread = latest seq − last_read − own messages after last_read; keep per-member counters of own messages… discuss.)
- **B1 across servers:** "Per-channel sequence with multiple writers?" (Atomic increment per channel in the DB; or a single writer per channel/partition.)

## Feature requests
1. **"Threads: replies to a message."** Strong answer: parent seq; separate unread counts per thread; history per thread.
2. **"Reactions."** Strong answer: dict message → emoji → set of users; idempotent add/remove.
3. **"@channel notifies everyone except the author, rate-limited."** Strong answer: expand members; cap per hour; respects mute settings.

## Scoring signals
- **Strong:** converts the example; pages through history; compares edit/delete permissions.
- **Weak:** only posting and reading one message.
