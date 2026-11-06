You are a senior Bloomberg engineer preparing to interview candidates on a practice pack: a small Python codebase with deliberately
planted bugs and no tests. The pack ships no answer key, so you are writing one. A strict mock interviewer will use your notes to
play the product manager and judge the candidate; a debrief writer will use your fixes and tests to teach the candidate afterwards.
Accuracy matters more than anything: every bug you list must be real, and every test must fail on the shipped code for that reason.

## The current directory

- `pack/`: the pack exactly as shipped. The candidate gets `README.md`, `CANDIDATE_BRIEF.md` (round 1), `SETUP.md`, `tickets/`
  (round 2) and `python/`. They do **not** get `PROJECT_MANAGER_NOTES.md` (questions a strong candidate should ask, so they must
  come up with these themselves) or `SELF_REVIEW_AFTER.md` (what strong candidates notice). Use both as hints, but verify
  everything in the code yourself: they can be incomplete.
- `fixed/`: a copy of `pack/python/`. You fix the bugs here.
- `check.py`: verifies your work. Run it with `{{python}} check.py` (it prints PASS/FAIL per test on the shipped code and on
  `fixed/`). Don't modify it. Don't modify anything in `pack/`.

## What to produce

1. **Find every planted bug.** Read all of `pack/python/` and the docs. A planted bug is a place where the code contradicts the brief,
   README rules, tickets or the PM-notes answers you'd give (missing state guards, idempotency gaps, off-by-ones, wrong comparisons,
   stale reads, broken invariants). There are usually 3–6. Don't invent bugs from style issues, and don't count behaviour the docs
   leave genuinely open.

2. **`fixed/`**: apply the narrowest fix for each bug to the files in `fixed/`. Don't refactor, rename or change public APIs.

3. **`test_hidden.py`** (in the current directory): pytest tests, imported the way a candidate would from inside `python/` (e.g.
   `from orders import OrderService` or `from payments.service import PaymentsService`; the pack's conftest.py puts `python/` on the
   path). Rules:
   - name every test `test_b<N>_<what>` where N is the bug number in NOTES.md (several tests per bug are fine);
   - each test must fail on the shipped code because of that bug only, and pass on `fixed/`;
   - every test must pass on `fixed/`; keep them small, deterministic (use the injected clock where there is one) and readable,
     with a one-line docstring saying what rule they check.

4. **`NOTES.md`** (in the current directory), in this exact structure (Markdown):

```
# R<round> · <codename> · <Domain title>: Interviewer Guide

<2–3 sentences: what the service is, its size, how the candidate gets in (round 1: the reported symptom; round 2: the tickets),
and how much is a pass (e.g. "Finding and fixing 3 of 5 with tests is solid").>

Starting ticket: <round 2 only: the ticket file to assign first, usually the clearest one; otherwise omit this line>

## PM answers
| Question | Answer |
|---|---|
<one row per question in PROJECT_MANAGER_NOTES.md, answered decisively as the PM, consistent with your fixes; plus 3–6 more rows for
other ambiguities a candidate might ask about (boundaries, errors vs no-ops, idempotency, ordering, what's out of scope).>

## Code map
<the modules, classes and methods, in one or two lines each, with where state lives.>

## Planted bugs (<count>)

### B1 · <short name>
- **Where:** `<file>`: `<function>`, with the offending expression quoted.
- **Rule broken:** <the doc sentence or ticket it contradicts, quoted; for round 2, name the ticket>.
- **Test:** <the scenario and the expected vs actual result>.
- **Fix:** <the minimal change>.

<…one subsection per bug…>

Hints: (1) <a level-1 hint pointing back to the docs in general terms>; (2) <a level-2 hint naming an area of the code, not the bug>

## Red herrings
<things that look wrong but are correct, and out-of-scope smells a strong candidate names but leaves alone.>

## Questions about the candidate's fixes (data structures)
<4–6 bullets: a question about the data structures and complexity in this code, with a strong answer in parentheses (complexity,
alternatives, trade-offs, what changes when it's concurrent or distributed).>

## Feature requests
<2–3 numbered realistic feature requests for this service, each with what a strong answer covers: clarifying questions, design,
data-structure changes, edge cases and tests.>

## Scoring signals
- **Strong:** <specific behaviours on this pack>
- **Weak:** <specific behaviours on this pack>
```

Iterate until `{{python}} check.py` reports that every test fails on the shipped code and passes on `fixed/`. When you finish,
reply with one line: the number of bugs and the test count.
