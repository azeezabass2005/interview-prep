# R2-01 · Research Portal: Interviewer Guide

A ~900-line Python API (no framework: sqlite3, a small router, middleware, a job queue) behind a Next.js front end. Five tickets,
each a different real backend failure. The candidate picks one; one ticket done properly with a test is a full pass. All bugs are
in the backend; `web/` is context only.

## Ticket map

| Ticket | Area | Real root cause | Where | Trap |
|---|---|---|---|---|
| RES-101 cross-client entitlements | Data access / authorization | SQL operator precedence: `org_id = ? AND starts_on <= ? AND ends_on > ? OR ends_on IS NULL` makes **every** open-ended subscription (any firm) match | `repositories/entitlements.py: sectors_for` | Adding an org check in `read_report` only: the list and the digest use the same query, so they'd still leak |
| RES-104 wrong firm's list | Caching | List cache key `reports:{sector}:{page}:{page_size}` has no org, but the result is entitlement-filtered | `services/reports.py: list_reports` | Disabling the cache (AC says keep it); clearing the cache per request; keying by user (works but kills the hit rate) |
| RES-110 duplicate on next page | Data access / pagination | Fetches `page_size + 1` rows to compute `has_more`, then returns all of them | `services/reports.py: list_reports` (`Page(rows, …)`) | Changing the LIMIT to `page_size` (then `has_more` is always false) or the OFFSET |
| RES-115 tokens in logs | Observability | Access log writes `query=dict(request.query)`; the PDF route authenticates with `?access_token=` | `middleware.py: access_log` | Header redaction already exists and works, so candidates look there first; dropping the query from logs entirely (AC: keep other params) |
| RES-120 missed digests | Background jobs | `send_digest` advances `last_digest_at` **before** sending, then swallows the send error, so the job is "done" and the reports are skipped forever | `services/digest.py: send_digest` | Only re-raising (job retries but `last_digest_at` already moved, so the retry sends nothing); retrying inside the handler with a loop (the worker already has backoff) |

## PM answers
| Question | Answer |
|---|---|
| Is `ends_on` inclusive or exclusive? | Exclusive. Entitled from `starts_on` up to but not including `ends_on`. |
| Should an unentitled report be 403 or 404? | Keep 403 for clients (the web app shows "not entitled"). Drafts are 404 to clients. |
| Can we just turn the list cache off? | No, it's the busiest endpoint. Keep it; correctness first, then hit rate. |
| How long can a list be stale after a publish? | Publishing/withdrawing should refresh lists immediately (that already works). |
| Should we log the PDF query string at all? | Yes, other params are used by dashboards; just never credentials. Treat `access_token`, `token`, `api_key` as credentials. |
| If a digest fails 4 times? | It goes to the dead-letter state (already supported); the next day's digest must still include those reports. |
| Can a user get the same report twice across digests? | No: each report once per user. |
| Can I change the web app? | Not needed for any ticket. |

## RES-101 · entitlement precedence
**Invariant:** a firm's readable sectors come only from *its own* active subscriptions.
**Fix:** `WHERE org_id = ? AND starts_on <= ? AND (ends_on > ? OR ends_on IS NULL)`.
**Test:** firm A Energy (term), firm B Tech (open-ended), Tech report → firm A gets 403 on read and doesn't see it in the list; firm B
can read it. Strong candidates also check the digest (same query) and say the fix in the repository covers read, list and digest.

## RES-104 · cache key
**Fix:** include the org (the thing the result depends on): `f"reports:{principal.org_id}:{sector or 'all'}:{page}:{page_size}"`.
Keep the `reports:` prefix so `delete_prefix("reports:")` on publish still invalidates. Internal users share one org, so they still
get hits.
**Test:** firm A (Energy) lists, then firm B (Rates) lists within the TTL → B sees only Rates; then a second B call is served from the
cache (no `FROM reports` statement). Strong: "a cache key must include every input that changes the result".

## RES-110 · page overflow
**Fix:** `Page(rows[:page_size], page, page_size, has_more=len(rows) > page_size)`.
**Test:** 25 reports, page 1 has 20 and `has_more`, page 2 has 5 and not `has_more`, no id on both pages. Exactly 20 → `has_more`
false. Strong: names the "fetch one extra" idiom and why the extra row must be dropped.

## RES-115 · tokens in logs
**Fix:** redact credential query params in the access log, e.g. a `SENSITIVE_QUERY = {"access_token", "token", "api_key"}` and
`query={k: ("[REDACTED]" if k.lower() in SENSITIVE_QUERY else v) for k, v in request.query.items()}`; ideally next to
`redact_headers` in `observability.py`.
**Test:** call the PDF route with `?access_token=…&utm=email` → the token string is nowhere in `logger.records`, `utm` still is,
the response is 200. Strong: greps the logs for the token value rather than checking one field; mentions the unhandled-error log
path (it logs `path`, not the query, so it's fine) and that tokens in URLs also leak via browser history and proxies (RES-118).

## RES-120 · digest
**Fix:** send first; only after Postbox accepts it, set `last_digest_at`; let `EmailError` propagate so the `Worker` retries with
backoff (don't catch, or log and re-raise). Better: use the newest report's `published_at` (or the time the reports were selected)
as the watermark, not "now", so a report published during the send isn't skipped.
**Test:** FakeTransport returns 503 then 202 → after the first run the job is `queued` (not done) and `last_digest_at` is unchanged;
advance past the backoff, run again → one email with the report, job done. Also: a second digest run doesn't resend it.
**Where people go wrong:** only removing the `try/except` (retry happens but sends nothing because the watermark already moved);
retry loops with `sleep` inside the handler.

## Red herrings
- `redact_headers` is correct: `Authorization` is redacted case-insensitively.
- The rate limiter keys by user when authenticated: correct.
- `ORDER BY published_at DESC, id DESC` already has a tie-breaker.
- `PostboxClient` classifies 429/5xx as retryable correctly.

## Questions about the candidate's fixes (data structures)
- **Cache:** "What's the hit rate impact of adding org to the key? What if you keyed by user?" (Per-org: one entry per firm per
  page; per-user: N× entries, lower hit rate. Key by the narrowest input that determines the result: the org's sector set; even
  better, key by the *sorted sector set*, so firms with the same entitlements share entries.)
- "With several API instances, each has its own in-process cache. What goes wrong on publish?" (Only the instance that handled the
  publish invalidates; others serve stale lists for up to 60 s. Shared cache (Redis) with versioned keys or pub/sub invalidation.)
- **SQL:** "How would you have caught RES-101 in review?" (Always parenthesise mixed AND/OR; a test per tenant boundary; row-level
  security or a repository helper that always applies the tenant filter.)
- **Pagination:** "Why does OFFSET get slow, and what's the alternative?" (OFFSET scans and discards rows: O(offset). Keyset/cursor
  pagination on `(published_at, id)` with an index is O(log n + page).)
- **Jobs:** "The digest job crashes after Postbox accepted the email but before `last_digest_at` is saved. What happens?" (At-least-
  once: the retry sends a duplicate. Use an idempotency key per (user, digest date) with Postbox, or an outbox table.)

## Feature requests
1. **"Let firms subscribe to individual analysts as well as sectors."** Strong: entitlement becomes a union of rules; a table
   `analyst_subscriptions`; the cache key must change (sector set alone no longer determines the list); tests at tenant boundaries.
2. **"Signed download links instead of tokens in URLs (RES-118)."** Strong: HMAC over (report id, user, expiry) with a server
   secret; short TTL; constant-time compare; no credential in logs or history; revocation trade-offs.
3. **"Real-time 'new report' notifications in the web app."** Strong: SSE/WebSocket fan-out per entitled sector, auth on connect,
   back-pressure, and why the digest stays as the source of truth.

## Scoring signals
- **Strong:** reproduces with a failing test through the HTTP layer (`World.call`) before changing code; for RES-101 finds the query
  by tracing list/read/digest to the shared repository; for RES-104 states "every input that changes the output must be in the key";
  for RES-120 reasons about at-least-once delivery and ordering of side effects.
- **Weak:** patches the symptom at one call site (e.g. a check in `read_report` only); disables the cache; removes logging of the
  whole query; makes the digest swallow errors differently; no test.
