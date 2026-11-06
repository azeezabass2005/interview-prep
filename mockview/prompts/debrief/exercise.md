Write the section "## 2. The exercise, solved: what a strong candidate does".

This is the most important section. Teach the candidate exactly how to solve this exercise, compared with what they did. Include:

### 2.1 Reading the spec
Break the spec into a numbered list of testable rules (one per rule sentence), highlighting the boundary words (at or, at least,
earliest, cancelled, same trader, rounded down…). Say which rules the candidate mentioned in their summary and which they missed.

### 2.2 Clarifying questions you should have asked
A table: the question to ask the PM, why it matters (which rule/bug it protects against), the PM's answer (from interviewer-notes.md),
and whether the candidate asked it (with timestamp). Cover every PM-table question plus any other ambiguity worth asking about
(e.g. precedence/priority rules, boundaries, rounding, what happens on errors). Then give the 2–3 questions that matter most and the
exact words to ask them.

### 2.3 A 30-minute plan
A minute-by-minute plan a strong candidate follows for this exercise (summary, questions, mapping the code with the AI assistant, the
example test, one bug at a time…), with the exact prompts to give the AI assistant at each step (in code blocks).

### 2.4 Every planted bug, one by one
For each bug in interviewer-notes.md (B1, B2, …), a subsection with:
- status for this candidate (found / fixed / missed / told by the interviewer), with timestamps;
- the spec sentence that reveals it, quoted;
- how to find it: what to test, where to look in the code, which line(s) and why they're wrong;
- the test to write, as complete Python code that would run in their session (`unittest` in `tests/` for the mock.py kit, pytest in a
  `python/test_*.py` file for practice packs; base it on reference-hidden-tests.py but
  write it the way a candidate would, with a clear name and an explanation of the expected failure);
- the minimal fix as a diff, and why it's minimal;
- how to verify it and what side effects to check;
- what in the candidate's actual run came closest, and the exact moment they could have caught it.

### 2.5 Red herrings and traps
What looks wrong but is correct, and how to avoid wasting time on it.
