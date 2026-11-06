# Vault

Vault is where our investment banking teams keep working documents: deal memos, models' notes and term sheets. Documents
live in a **workspace** (a team); each is private to its owner unless shared with named colleagues (view or edit) or through a
**share link** that works without logging in, for sending to clients. The web app (`web/`, Next.js) is the main client.
Several API instances run behind a load balancer and share one database.

You'll investigate one reported problem from `tickets/`, make a bounded change, and prove it with a test.
Completion percentage is not the signal: one ticket done properly is a full pass.

## Running

```bash
python -m unittest discover -s tests -v   # the test suite (standard library only)
python -m vault.seed && python server.py  # demo users + tokens, then the API on :8000
cd web && npm install && npm run dev      # optional: the web app on :3000
```

## Architecture

```text
vault/
  wiring.py                    builds the app and middleware stack (share links are public paths)
  limits.py                    request body size limit middleware
  services/documents.py        documents, sharing, previews (cached), search, cursor pagination, share links
  repositories/documents.py    SQL for documents, ACL and share links; ACCESSIBLE is the "may this user read it" filter
  config.py                    size, cache and link limits
  api/handlers.py              endpoints
  middleware.py, auth.py, cache.py, db.py, app.py, router.py, http.py, observability.py, ratelimit.py, clock.py, ids.py, errors.py
web/                           Next.js web app (you shouldn't need to change it)
```

## Rules

- A user can read a document if they own it or it's shared with them. **Nothing about a document they can't read (not even its
  title) may be revealed to them.** Deal names are confidential (Compliance policy C-12).
- Share links expire at the time chosen when they were created (at most 30 days) and can be revoked.
- Document lists are newest first, 20 per page, with an opaque `next_cursor`. Every accessible document appears exactly once
  across the pages.
- Previews are slow to render, so they're cached for 10 minutes, but a preview must always show the document's current
  version.
- Request bodies over 1 MB are rejected with `413` before any processing.
