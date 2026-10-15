# Team Chat Service

Backend for an internal chat app (1:1 and group conversations). Phones and laptops send messages through the API; clients
**retry** sends on flaky networks using a client-generated `client_msg_id`. Each user may be signed in on several devices.
Several API instances share one database.

Pick one ticket from `tickets/`, make a bounded change and prove it. One ticket done properly is a full pass.

## Running

```
python -m unittest discover -s tests -v
```

## Layout

```
chat/api/handlers.py              ChatApi
chat/services/messaging.py        send, recent, scroll-back history
chat/services/read_state.py       mark-read and unread counts
chat/services/moderation.py       masks banned words
chat/repositories/*.py            conversations, members, messages
chat/db.py, clock.py, errors.py, models.py, config.py
```

## Rules

- Every message gets a **server sequence number** (`seq`) per conversation, assigned when the server accepts it (1, 2, 3, …).
  **`seq` is the only ordering clients should trust.** `client_sent_at` comes from the device clock and is informational only.
- One sender + one conversation + one `client_msg_id` = **one message**, even if the client retries concurrently.
- **Read state** is per user (not per device): `last_read_seq`. A user's read position only moves **forward**.
  `unread = messages with seq > last_read_seq that the user didn't send`.
- **Scroll-back:** `GET /conversations/{id}/messages?before=<seq>&limit=n` returns the **n messages immediately before** `seq`,
  oldest first.
