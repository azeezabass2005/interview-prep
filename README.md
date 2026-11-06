# Bloomberg AI-Assisted Coding Rounds: Mock Interview Kit

60 practice exercises (50 in Round 1, 10 larger services in Round 2) built to the format described in the Bloomberg AI interview prep workshop
(*"What the Questions Look Like"* and *"How to Approach and Solve Them"*, plus the workshop slides):

| Folder | Count | Format |
|---|---|---|
| `round-1/` | 50 | **Spec + single-file codebase.** A `SPEC.md` (rules, a worked example; no questions, no tickets) and **one Python file** (~75–125 lines, no comments) that claims to implement it, with **exactly 5 planted bugs** where the code doesn't match the spec and only **one passing test**. You find the bugs by writing tests from the spec. Covers all 50 topics below. |
| `round-2/` | 10 | **Full-stack services with real backend bugs.** Each is a product with a Next.js front end (`web/`, context only) on a plain-Python backend (standard library: `sqlite3`, hand-written router, middleware, repositories, TTL cache, rate limiter, durable job queue, third-party HTTP adapters), ~500–900 lines, a passing test suite and **5 tickets**. Every ticket is a different real backend failure: authorization (IDOR, role vs. object), rate limiting, data access (SQL precedence, injection, N+1, transactions, pagination, soft deletes), caching (keys, TTL units, mutation, invalidation), background jobs (idempotency, claiming, backoff, poison messages), observability (secrets/PII in logs, metrics, tracing), middleware and error handling, and adapters (retries, idempotency keys, webhooks, error classification). |
| `interviewer-notes/` | 60 | The interviewer's guide: session timeline, PM answers to clarifying questions, code map, **every planted bug** (location, symptom, root cause, minimal fix, the test to write, hints), red herrings, **data-structure and complexity questions about the candidate's fixes** (alternatives, time/space trade-offs), **feature requests** to discuss after the fixes, scoring signals, plus `hidden_tests.py` and reference `fixes.py`. |

Everything is Python 3 **standard library only** (no installs, the same constraint as the real interview). Tests use `unittest`.

> **Never open this root folder with your AI agent.** The agent can read `interviewer-notes/`. Always start a session (below)
> and open **only the session folder**.

---

## Running a mock

```bash
cd ~/Projects/interview-prep
python mock.py list                 # all exercises
python mock.py start 1              # random round-1 exercise
python mock.py start 2 03           # a specific round-2 service (03 = market data API)
```

`start` copies the exercise into `sessions/<timestamp>-…/` and commits the starting point to git, so you can review **your diff**
at the end. Open that folder in your IDE with your agent (Copilot / Claude Code / Cursor). Then:

1. **5 min:** walk through your resume and one problem you solved, out loud (rounds 1 and 2 open with this).
2. **Round 1 (50 min):** read `SPEC.md`, summarise it, ask your clarifying questions, map the code with the agent, then hunt for
   places where the code doesn't match the spec: write a failing test, explain it, make a minimal fix, repeat. The interviewer then asks
   about the data structures in your fixes and gives you a feature request to design.
   **Round 2 (50 min):** read `README.md` and `tickets/`, pick **one** ticket (or take the one the interviewer gives you) and take it
   all the way: reproduce it with a failing test, find the root cause, make the narrowest fix, prove it. `web/` is the Next.js front
   end; the bugs are all in the Python backend. Talk the whole time; record yourself if you can.
3. Clarifying questions: say them out loud. Solo? `python mock.py pm <session>` prints the PM's answers (every spec-based exercise)
   **without** the bug list. Round 2 tickets have a PM sheet too (`python mock.py pm`): state your assumption and question the acceptance criteria.
4. Finish:

```bash
python mock.py grade sessions/<session>   # your tests, hidden checks (one per planted issue), diff stat
python mock.py notes sessions/<session>   # full interviewer notes: read only after grading
```

Then score yourself with [`SCORECARD.md`](SCORECARD.md). **Hidden checks are a guide, not the grade.** The workshop was explicit that
the grade is your reasoning, judgement and communication while using AI, and that finishing everything is not the signal.

### With a friend as interviewer
Give them `interviewer-notes/<round>/<exercise>/NOTES.md`. They play the product manager using the "PM answers" table, ask the
follow-up questions at the end, and fill in `SCORECARD.md` while you work.

---

## The workflow you're practising (from the workshop)

**Round 1: read the spec → inspect the code → find gaps/bugs → fix + test**
- Only one test exists and it passes; in many exercises even the spec's worked example passes on the buggy code. Derive edge cases from
  every rule and boundary word in the spec ("at least", "more than", "on or before", "rounded down").
- Summarise the spec into numbered requirements; list ambiguities. *"Do not look at the code yet."*
- Map entities and data flow; ask the agent which requirements the tests **don't** cover.
- Walk requirement by requirement: implemented / implemented wrongly / missing. Verify every agent claim in the code.
- One bug at a time: state it as *issue, line, why*; write a test that **fails for one clear reason**; minimal patch; predict, then run.
- Turn the spec's worked example into a test early. In many of these exercises it isn't in the visible suite.

**Round 2: read ticket → define success → map the path → name the invariant → small plan → patch small → prove it → review the diff**
- *"Summarize the reported behavior, the acceptance criteria, and what is explicitly out of scope. Do not propose a fix yet."*
- *"Starting at X, trace … Name the files, functions and data fields. Do not modify code."*
- Name the invariant, then judge options against it (second lookup? process lock? the layer that owns the invariant?).
- Ask whether the acceptance criteria are even right. Some tickets here deliberately point at the wrong fix.
- Deterministic test of the real condition (for races: pause both calls at the vulnerable point with a `threading.Barrier`).
- Explain every line of the final diff. Call out remaining risks.

**Prompt anatomy:** a starting point + one goal + the output you want + a boundary ("don't change code yet").

---

## Exercise index

### Round 1: spec + single file (50)
| # | Exercise | Focus |
|---|---|---|
| 01 | pot-luck | The workshop's own example: draws, entries, tiers, rollover |
| 02 | brokerage-commission | Commission bands, min/cap, regulatory fee, busted trades |
| 03 | parking-garage | Reserved spaces, hourly/daily charges, validation |
| 04 | dividend-reinvestment | Record date, withholding, DRIP fractional shares |
| 05 | order-matching | Limit order book: price-time priority, IOC, self-trade |
| 06 | group-tab | Four split modes, payments, settle-up |
| 07 | tournament-prizes | Re-entries, guarantee, payout brackets, eliminations |
| 08 | miles-ledger | Earning, status tiers, expiry, transfer limits |
| 09 | silent-auction | Proxy bidding, increments, soft close, reserve |
| 10 | ride-fare | Locked surge, minimum fare, waiting, promos, payouts |
| 11 | ipo-allocation | Tranches, pro rata with lots, priority on amend |
| 12 | bowling-score | Frame scoring, unknown frames, handicaps |
| 13 | payroll-overtime | Breaks, daily/weekly overtime, rate history |
| 14 | solar-net-metering | Register rollover, prorated tiers, kWh bank |
| 15 | card-statement | ADB interest, grace, payment order, minimum |
| 16 | bond-accrued-interest | T+2 with holidays, 30/360 vs ACT/360, schedules |
| 17 | margin-call | Haircuts, concentration, staleness, calls |
| 18 | fx-converter | Cross rates, spread, minor units, daily limit |
| 19 | api-quota | Token bucket, monthly units, overage |
| 20 | hotel-rates | Nights, weekend rates, availability, cancellation |
| 21 | tip-pool | Fees, eligibility, weighted shares, leftover cents |
| 22 | gradebook | Late penalty, excused, drop lowest, letters |
| 23 | fifo-inventory | FIFO lots, all-or-nothing, transfers, returns |
| 24 | crowdfunding | Tier slots, goal, retries, fees |
| 25 | portfolio-rebalancer | Drift band, cash buffer, restrictions, rounding |
| 26 | parcel-shipping | Billable weight, fuel, business days, free shipping |
| 27 | league-table | Standings, tie-breaks, corrections, deductions, form |
| 28 | library-fines | Due dates, caps, renewals, holds queue |
| 29 | class-waitlist | Waitlist promotion, late cancel, credits |
| 30 | capped-index | Float adjustment, iterative capping, residue, turnover |
| 31 | meeting-calendar | The workshop calendar: retries, conflicts, time zones |
| 32 | order-management | Order validation, duplicate executions, average price |
| 33 | market-data-cache | TTL, LRU, stale fallback, normalisation |
| 34 | price-alerts | Crossing detection, one-shot, quiet hours, caps |
| 35 | payments-ledger | Double entry, holds, idempotency, fees, reversals |
| 36 | event-ticketing | Seat holds, single-gap rule, limits, refunds |
| 37 | link-shortener | Base 62 codes, aliases, dedupe, expiry |
| 38 | job-queue | Priorities, delays, leases, retries |
| 39 | inventory-reservations | Expiring reservations, all-or-nothing checkout |
| 40 | chat-messaging | Per-channel sequence, unread, pagination, mentions |
| 41 | news-feed | Mutes, syndication dedupe, cursor pagination |
| 42 | api-gateway | Check order, routing, rate limits, circuit breaker |
| 43 | user-accounts | Unique e-mails, lockout, reset tokens |
| 44 | expense-approvals | Approval chains, ordering, resubmission |
| 45 | trade-settlement | T+1, netting, fails, reconciliation |
| 46 | pnl-service | FIFO lots, commissions, splits |
| 47 | feature-flags | Rule order, hashing buckets, prerequisites |
| 48 | room-booking | Office time zones, no-shows, recurring bookings |
| 49 | leaderboard | Valuation, qualification, tie-breaks, paging |
| 50 | document-versioning | Optimistic concurrency, restore, retention, publishing |

### Round 2: full-stack services, 5 tickets each
| # | Service | Tickets (the real root-cause area) |
|---|---|---|
| 01 | research-portal | entitlement SQL precedence · list cache key missing the client firm · page overlap · tokens in access logs · digest job marks "sent" before sending |
| 02 | payments-gateway | retry without a stable idempotency key (double charge) · retrying card declines · webhook HMAC over re-serialised JSON · JPY minor units · processor outage → 500 |
| 03 | market-data-api | rate limiter before auth (shared bucket) · cache TTL ms vs s · mutating a cached object · SQL injection in search · errors missing from metrics (middleware order) |
| 04 | trade-blotter | desk head amends other desks (object authorization) · two transactions for one booking · N+1 queries · business date vs UTC in the EOD job · ValueError → 500 |
| 05 | alerts-delivery | job claimed by two workers · backoff max/min · 429 treated as permanent · IDOR via `?user_id=` · phone numbers in logs |
| 06 | identity-service | reusable reset links · sessions with no absolute lifetime · lockout bypass by email case · account enumeration · stale permission cache |
| 07 | billing-service | non-idempotent invoice run · `BETWEEN` double-counts usage · float/banker's rounding · tax adapter outage stops the run · duplicate payment webhooks |
| 08 | document-sharing | expired share links · search ignores the ACL · cursor skips equal timestamps · preview cache ignores the version · body limit trusts Content-Length |
| 09 | api-gateway | breaker never resets · request id not propagated · client tokens forwarded to a partner · sliding limiter counts rejections · retrying POSTs |
| 10 | expense-reports | cross-team approval · FX cache key missing the date · poison receipt blocks the OCR batch · soft-deleted lines in totals · mass assignment |

---

## Suggested plan
- **Week 1:** one or two Round 1 exercises per day (start with 01 Pot Luck, the workshop example, and 31, the workshop calendar).
- **Week 2+:** Round 2 services, one ticket per session. Do a *different* ticket of a service you've seen before only after a week:
  the point is navigating unfamiliar code. Across the 10 services, every common backend failure area comes up several times.
- After each session: re-read your diff, the notes and the scorecard; write down one thing you'll do differently.
- Also practise in the real environment: **HackerRank mock interviews** (named in the workshop).

## Honest caveats
- Real codebases may be bigger. Round 2 services are ~500–900 lines of Python plus a small Next.js app, so that every ticket stays
  verifiable. The skill (don't read everything; trace one path; reproduce with a test) is the same.
- Round 1 code has no comments or docstrings, matching what candidates reported. Round 2 services read like real code (a few
  docstrings), but nothing points at a bug.
- Some exercises (Round 1 #31, #34, #48) use `zoneinfo`, which needs the system time-zone database (standard on Linux/macOS).
- Maintainer self-check: `python mock.py verify` proves for every exercise that the visible tests pass on the buggy code, every hidden
  check fails on it, and everything passes after the reference fixes.
- Your own practice edits from 17 Oct (made directly in the old order-matching exercise) were kept in
  `sessions/your-practice-order-matching-2026-10-17/`.
- The previous 50 Round 2 exercises (tickets 01–20 and multi-module specs 21–50) are in git history if you want them back:
  `git checkout HEAD -- round-2 interviewer-notes/round-2` restores them (move the new ones aside first).
