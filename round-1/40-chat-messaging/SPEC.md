# Chat Messaging

A team chat backend stores channel messages, tracks what each member has read, and sends mention notifications. `chat.py` holds the logic.

## Messages

- Only channel members can post. Every message gets a **sequence number per channel**, starting at 1 in each channel.
- Clients send a **client message id**; a repeated id from the same author in the same channel returns the original message (no duplicate).
- Authors can **edit** their own messages within **15 minutes** of posting, and delete them (the text becomes `[deleted]`). Nobody else can.

## Reading

- `mark_read(channel, member, seq)` records the last message a member has read.
- **Unread count** = messages after the member's last-read sequence, **not counting their own**.
- `history(channel, before=None, limit=50)` returns messages **newest first**: the newest ones, or the ones with sequence **strictly less
  than** `before` (for loading older pages). `limit` is at most 100.

## Mentions

`@name` in a message notifies that person **if they're a member of the channel**. Each person is notified once per message.

## Example

#general (Ana, Ben). Ana posts "hi @ben" (seq 1, Ben notified), Ben posts "hey" (seq 2). Ana's unread count: **1**; Ben's: **1**.
