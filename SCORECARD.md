# Mock Interview Scorecard

Based on the workshop's **"What We Will Be Assessing"** slide. Score each row 1–4 straight after the session, from your recording or
your interviewer friend's notes. The hidden checks from `mock.py grade` inform row 3 but don't decide anything on their own.

Exercise: ______________________ Date: __________ Elapsed: _____ min

| # | Criterion (from the slide) | 1 · Miss | 2 · Weak | 3 · Solid | 4 · Strong | Score |
|---|---|---|---|---|---|---|
| 1 | **Understand, explain and work with code**, including AI-generated code | Couldn't explain what the code did | Explained with the agent's words | Explained the flow and the bug in own words | Explained the root cause as "issue, line, why" and predicted side effects | |
| 2 | **Use AI tools effectively and critically** | One-shot "fix the repo", or avoided the agent | Broad prompts, accepted output unchecked | Single-goal prompts with boundaries; verified claims in code | Challenged a wrong agent claim or a weak proposal, and showed why | |
| 3 | **Testing, verification, technical judgement** | No new tests | Tests that pass for the wrong reason, or "test that it's fixed" | Each fix has a test that fails before for one clear reason | Reproduced the real condition (e.g. paused race); predicted results before running; reviewed the final diff | |
| 4 | **Problem solving, planning, system design** | Jumped into edits | Fixed symptoms | Named the invariant / requirement before choosing a fix | Picked the layer that owns the invariant; rejected weaker options with reasons; questioned wrong acceptance criteria | |
| 5 | **Communicate thinking and decisions clearly** | Went silent | Narrated actions, not reasons | Hypothesis before each prompt; explained each decision | Interviewer never out of the loop; clean wrap-up of risks and next steps | |
| 6 | **Collaboration** | Ignored the interviewer | Asked no clarifying questions | Asked targeted clarifying questions; "I'm assuming X, I'll add a test" | Treated the interviewer as PM; scoped work with them; left out-of-scope issues alone but named them | |

**Total: ___ / 24.** The workshop's bar is roughly "3 everywhere" (one ticket or a few bugs done properly).

## Behaviour checklist (from the workshop's dos and don'ts)

- [ ] Summarised the spec/ticket and confirmed my reading before coding
- [ ] Asked clarifying questions, or stated assumptions and pinned them with tests
- [ ] Used the agent to map the code before asking it to change anything
- [ ] Verified at least one agent claim directly in the code
- [ ] Never delegated the whole task in one prompt
- [ ] Changed the smallest piece of code that owns the problem (no refactors)
- [ ] Turned the spec's worked example / ticket's repro into a test
- [ ] Predicted each test's result before running it
- [ ] Read the final diff and explained every retained change
- [ ] Checked the fix against every acceptance criterion **and** questioned the criteria
- [ ] Named remaining risks and what I'd do with more time
- [ ] Never went quiet for more than ~30 seconds

## Post-mortem (2 minutes)

- The moment I lost time: …
- The prompt that worked best: …
- One agent claim I should have checked (or did check): …
- Next session I will: …
