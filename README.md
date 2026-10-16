# Bloomberg AI-Assisted Coding Rounds: Mock Interview Kit

50 practice exercises built to the format described in the Bloomberg AI interview prep workshop
(*"What the Questions Look Like"* and *"How to Approach and Solve Them"*, plus the workshop slides):

| Folder | Count | Format |
|---|---|---|
| `round-1/` | 30 | **Spec + codebase.** A `SPEC.md` describing a business system (rules, data model, worked example; no questions, no tickets) and a multi-module Python package (models, store, services, API, reporting; ~150–450 lines, no comments) that claims to implement it. Each has **exactly 5 planted bugs** where the code doesn't match the spec, and only **one passing test**. You find the bugs by writing tests from the spec. |
| `round-2/` | 20 | **README + tickets + multi-module service.** API → services → repositories → SQLite, plus noise modules. Four realistic tickets per service (bug reports / client complaints with steps to reproduce and acceptance criteria). Several are concurrency problems across instances; several have **acceptance criteria that blame the wrong root cause**; each has related issues that are **out of scope**. |
| `interviewer-notes/` | 50 | The interviewer's guide: session timeline, PM answers to clarifying questions, code map, **every planted bug** (location, symptom, root cause, minimal fix, the test to write, hints), red herrings, **data-structure and complexity questions about the candidate's fixes** (alternatives, time/space trade-offs), **feature requests** to discuss after the fixes, scoring signals, plus `hidden_tests.py` and reference `fixes.py`. |

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
```

`start` copies the exercise into `sessions/<timestamp>-…/` and commits the starting point to git, so you can review **your diff**
at the end. Open that folder in your IDE with your agent (Copilot / Claude Code / Cursor). Then:

1. **5 min:** walk through your resume and one problem you solved, out loud (rounds 1 and 2 open with this).
2. **Round 1 (50 min):** read `SPEC.md`, summarise it, ask your clarifying questions, map the code with the agent, then hunt for
   places where the code doesn't match the spec: write a failing test, explain it, make a minimal fix, repeat. The interviewer then asks
   about the data structures in your fixes and gives you a feature request to design.
   **Round 2 (50 min):** read `README.md` and `tickets/`, pick **one** ticket, take it all the way. Talk the whole time; record yourself if you can.
3. Clarifying questions: say them out loud. Solo? `python mock.py pm <session>` prints the PM's answers (round 1) **without** the bug list.
   Round 2 has no PM sheet: state your assumption and question the acceptance criteria.
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

### Round 1: spec + codebase
| # | Exercise | System |
|---|---|---|
| 01 | pot-luck | The workshop's own example, extended: multi-draw fundraiser with entries, limits, cancellations, rollover |
| 02 | brokerage-commission | Brokerage fee engine: equity tiers, options, regulatory fee, busted trades, monthly statements |
| 03 | parking-garage | Garage operations: gates, capacity with reserved spaces, validations, passes, pricing |
| 04 | dividend-reinvestment | DRIP processor: share register, withholding by country, enrolment history, reinvestment |
| 05 | order-matching | Mini exchange: limit and IOC orders, amend/cancel, trade tape, depth |
| 06 | group-tab | Group expenses: four split modes, edits/deletes, payments, settle-up suggestions |
| 07 | tournament-prizes | Card-room tournament: late registration, re-entries, eliminations, prize pool, bounties |
| 08 | miles-ledger | Frequent flyer program: earning, status tiers, expiry, redemption, transfers |
| 09 | silent-auction | Charity auction: proxy bidding, increment bands, soft close, invoices |
| 10 | ride-fare | Ride-hailing billing: locked surge, trip lifecycle, wait time, promos, driver payouts |
| 11 | ipo-allocation | IPO bookbuilding: price limits, retail/institutional tranches, amendments, allocation |
| 12 | bowling-score | Bowling league: game scoring, handicaps, team points |
| 13 | payroll-overtime | Weekly payroll run: shifts, meal breaks, rate changes, daily/weekly overtime |
| 14 | solar-net-metering | Utility billing: cumulative registers, prorated tiers, banking, true-up |
| 15 | card-statement | Credit card billing cycles: ADB interest, grace, payment allocation, fees |
| 16 | bond-accrued-interest | Bond trade booking: schedules, holidays, 30/360 and ACT/360 accrued |
| 17 | margin-call | Prime brokerage margin engine: haircuts, staleness, calls, deposits, liquidation |
| 18 | fx-converter | FX payments: rate book, quotes with expiry, booking, daily limits |
| 19 | api-quota | Market data API metering: token buckets, monthly allowances, invoices |
| 20 | hotel-rates | Hotel reservations: inventory per night, rate plans, pricing, cancellation |
| 21 | tip-pool | Restaurant tip pools: lunch/dinner pools, eligibility, weights, statements |
| 22 | gradebook | Course gradebook: submissions, late penalties, excusals, letter grades |
| 23 | fifo-inventory | Multi-warehouse FIFO inventory: shipments, transfers, returns, valuation |
| 24 | crowdfunding | Crowdfunding: tiers, pledge changes, settlement with failed charges, fees |
| 25 | portfolio-rebalancer | Robo-advisor: models, restrictions, rebalance planning |
| 26 | parcel-shipping | Checkout shipping: two carriers, dim weight, surcharges, delivery estimates |
| 27 | league-table | League standings: fixtures, corrections, tie-breakers, form guide |
| 28 | library-fines | Library circulation: branch calendars, holds, renewals, fines |
| 29 | class-waitlist | Fitness studio: plans and credits, priority waitlist, promotion, late cancels |
| 30 | capped-index | Index rebalance: eligibility, float adjustment, iterative capping, turnover |

### Round 2: tickets + multi-module service
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

---

## Suggested plan
- **Week 1:** one Round 1 per day (start with 01 Pot Luck, which is the workshop example), then R2-01 (the workshop calendar ticket).
- **Week 2+:** alternate one Round 1 and one Round 2 ticket per day. For Round 2, do a *different* ticket of a service you've seen
  before only after a week. The point is navigating unfamiliar code.
- After each session: re-read your diff, the notes and the scorecard; write down one thing you'll do differently.
- Also practise in the real environment: **HackerRank mock interviews** (named in the workshop).

## Honest caveats
- Real codebases may be bigger (Round 2 likely thousands of lines, possibly with a front end). These are 150–750 lines so that 50 of them
  stay verifiable. The skill (don't read everything; trace one path; derive tests from the spec) is the same.
- None of the code has comments or docstrings, matching what candidates reported from the real interviews.
- `round-2` exercises use `zoneinfo`, which needs the system time-zone database (standard on Linux/macOS).
- Maintainer self-check: `python mock.py verify` proves for every exercise that the visible tests pass on the buggy code, every hidden
  check fails on it, and everything passes after the reference fixes.
