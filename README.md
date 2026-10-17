# Bloomberg AI-Assisted Coding Rounds: Mock Interview Kit

100 practice exercises (50 per round) built to the format described in the Bloomberg AI interview prep workshop
(*"What the Questions Look Like"* and *"How to Approach and Solve Them"*, plus the workshop slides):

| Folder | Count | Format |
|---|---|---|
| `round-1/` | 50 | **Spec + single-file codebase.** A `SPEC.md` (rules, a worked example; no questions, no tickets) and **one Python file** (~75–125 lines, no comments) that claims to implement it, with **exactly 5 planted bugs** where the code doesn't match the spec and only **one passing test**. You find the bugs by writing tests from the spec. Covers all 50 topics below. |
| `round-2/` | 50 | **Bigger codebases.** **01–20:** README + tickets + a multi-module service (API → services → repositories → SQLite, plus noise modules); four realistic tickets each, several concurrency problems across instances, several with **acceptance criteria that blame the wrong root cause**, out-of-scope issues. **21–50:** spec + a **multi-module package** (models, store, services, API, reporting; ~150–450 lines), one passing test, 5 bugs: the harder, multi-file version of Round 1 #01–30. |
| `interviewer-notes/` | 100 | The interviewer's guide: session timeline, PM answers to clarifying questions, code map, **every planted bug** (location, symptom, root cause, minimal fix, the test to write, hints), red herrings, **data-structure and complexity questions about the candidate's fixes** (alternatives, time/space trade-offs), **feature requests** to discuss after the fixes, scoring signals, plus `hidden_tests.py` and reference `fixes.py`. |

Everything is Python 3 **standard library only** (no installs, the same constraint as the real interview). Tests use `unittest`.

> **Never open this root folder with your AI agent.** The agent can read `interviewer-notes/`. Always start a session (below)
> and open **only the session folder**.

---

## Running a mock

```bash
cd ~/Projects/interview-prep
python mock.py list                 # all exercises
python mock.py start 1              # random round-1 exercise
python mock.py start 2 01           # a specific round-2 exercise (01 = the workshop's calendar ticket)
python mock.py start 2 21           # round-2 multi-module spec exercise (the harder Pot Luck)
```

`start` copies the exercise into `sessions/<timestamp>-…/` and commits the starting point to git, so you can review **your diff**
at the end. Open that folder in your IDE with your agent (Copilot / Claude Code / Cursor). Then:

1. **5 min:** walk through your resume and one problem you solved, out loud (rounds 1 and 2 open with this).
2. **Round 1 (50 min):** read `SPEC.md`, summarise it, ask your clarifying questions, map the code with the agent, then hunt for
   places where the code doesn't match the spec: write a failing test, explain it, make a minimal fix, repeat. The interviewer then asks
   about the data structures in your fixes and gives you a feature request to design.
   **Round 2 (50 min):** for 01–20, read `README.md` and `tickets/`, pick **one** ticket and take it all the way; for 21–50, it's the
   Round 1 workflow on a multi-module codebase. Talk the whole time; record yourself if you can.
3. Clarifying questions: say them out loud. Solo? `python mock.py pm <session>` prints the PM's answers (every spec-based exercise)
   **without** the bug list. Ticket exercises (Round 2 01–20) have no PM sheet: state your assumption and question the acceptance criteria.
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

### Round 2: tickets + multi-module service (01–20)
| # | Exercise | Service |
|---|---|---|
| 01 | meeting-calendar | **The workshop's "Blike Moomberg's Calendar"** (includes `CAL-TICKET-duplicate-request`) |
| 02 | order-management | Equity order management system |
| 03 | market-data-cache | Quote service with per-instance cache |
| 04 | price-alerts | Price alerts: evaluators + delivery workers |
| 05 | payments-ledger | Wallet ledger with invariants |
| 06 | event-ticketing | Reserved-seat box office |
| 07 | link-shortener | Internal URL shortener |
| 08 | job-queue | Durable background job queue |
| 09 | inventory-reservations | E-commerce stock reservations |
| 10 | chat-messaging | Team chat backend |
| 11 | news-feed | News aggregator and paged feed |
| 12 | api-gateway | Rate-limiting API gateway |
| 13 | user-accounts | Sign-up, login lockout, password reset |
| 14 | expense-approvals | Expense approval workflow |
| 15 | trade-settlement | Post-trade settlement and reconciliation |
| 16 | pnl-service | Portfolio P&L with lots and splits |
| 17 | feature-flags | Feature flag evaluation |
| 18 | room-booking | Global meeting-room booking |
| 19 | leaderboard | Trading competition leaderboard |
| 20 | document-versioning | Versioned research documents |

### Round 2: spec + multi-module package (21–50)
| # | Exercise | System |
|---|---|---|
| 21 | pot-luck | The workshop's own example, extended: multi-draw fundraiser with entries, limits, cancellations, rollover |
| 22 | brokerage-commission | Brokerage fee engine: equity tiers, options, regulatory fee, busted trades, monthly statements |
| 23 | parking-garage | Garage operations: gates, capacity with reserved spaces, validations, passes, pricing |
| 24 | dividend-reinvestment | DRIP processor: share register, withholding by country, enrolment history, reinvestment |
| 25 | order-matching | Mini exchange: limit and IOC orders, amend/cancel, trade tape, depth |
| 26 | group-tab | Group expenses: four split modes, edits/deletes, payments, settle-up suggestions |
| 27 | tournament-prizes | Card-room tournament: late registration, re-entries, eliminations, prize pool, bounties |
| 28 | miles-ledger | Frequent flyer program: earning, status tiers, expiry, redemption, transfers |
| 29 | silent-auction | Charity auction: proxy bidding, increment bands, soft close, invoices |
| 30 | ride-fare | Ride-hailing billing: locked surge, trip lifecycle, wait time, promos, driver payouts |
| 31 | ipo-allocation | IPO bookbuilding: price limits, retail/institutional tranches, amendments, allocation |
| 32 | bowling-score | Bowling league: game scoring, handicaps, team points |
| 33 | payroll-overtime | Weekly payroll run: shifts, meal breaks, rate changes, daily/weekly overtime |
| 34 | solar-net-metering | Utility billing: cumulative registers, prorated tiers, banking, true-up |
| 35 | card-statement | Credit card billing cycles: ADB interest, grace, payment allocation, fees |
| 36 | bond-accrued-interest | Bond trade booking: schedules, holidays, 30/360 and ACT/360 accrued |
| 37 | margin-call | Prime brokerage margin engine: haircuts, staleness, calls, deposits, liquidation |
| 38 | fx-converter | FX payments: rate book, quotes with expiry, booking, daily limits |
| 39 | api-quota | Market data API metering: token buckets, monthly allowances, invoices |
| 40 | hotel-rates | Hotel reservations: inventory per night, rate plans, pricing, cancellation |
| 41 | tip-pool | Restaurant tip pools: lunch/dinner pools, eligibility, weights, statements |
| 42 | gradebook | Course gradebook: submissions, late penalties, excusals, letter grades |
| 43 | fifo-inventory | Multi-warehouse FIFO inventory: shipments, transfers, returns, valuation |
| 44 | crowdfunding | Crowdfunding: tiers, pledge changes, settlement with failed charges, fees |
| 45 | portfolio-rebalancer | Robo-advisor: models, restrictions, rebalance planning |
| 46 | parcel-shipping | Checkout shipping: two carriers, dim weight, surcharges, delivery estimates |
| 47 | league-table | League standings: fixtures, corrections, tie-breakers, form guide |
| 48 | library-fines | Library circulation: branch calendars, holds, renewals, fines |
| 49 | class-waitlist | Fitness studio: plans and credits, priority waitlist, promotion, late cancels |
| 50 | capped-index | Index rebalance: eligibility, float adjustment, iterative capping, turnover |

---

## Suggested plan
- **Week 1:** one or two Round 1 exercises per day (start with 01 Pot Luck, the workshop example, and 31, the workshop calendar).
- **Week 2:** Round 2 21–50: the same topics as Round 1 01–30, but spread across several modules (do the Round 1 version of a topic
  first, then its Round 2 version a few days later).
- **Week 3+:** Round 2 tickets (01–20). Do a *different* ticket of a service you've seen before only after a week. The point is
  navigating unfamiliar code.
- After each session: re-read your diff, the notes and the scorecard; write down one thing you'll do differently.
- Also practise in the real environment: **HackerRank mock interviews** (named in the workshop).

## Honest caveats
- Real codebases may be bigger (Round 2 likely thousands of lines, possibly with a front end). These are 75–750 lines so that 100 of them
  stay verifiable. The skill (don't read everything; trace one path; derive tests from the spec) is the same.
- None of the code has comments or docstrings, matching what candidates reported from the real interviews.
- Some exercises (Round 1 #31, #34, #48 and several Round 2 tickets) use `zoneinfo`, which needs the system time-zone database (standard on Linux/macOS).
- Maintainer self-check: `python mock.py verify` proves for every exercise that the visible tests pass on the buggy code, every hidden
  check fails on it, and everything passes after the reference fixes.
- Your own practice edits from 17 Oct (made directly in the old order-matching exercise) were kept in
  `sessions/your-practice-order-matching-2026-10-17/`; the exercise itself (now Round 2 #25) was restored to its clean state.
