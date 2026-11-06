Your task: score this interview. Read the files, then respond with ONLY a JSON object inside <scores></scores>, nothing else.

Score each criterion 1–4 following scorecard.md (1 miss, 2 weak, 3 solid, 4 strong), or null if it didn't happen. Be calibrated:
3 means "meets the Bloomberg bar", 4 is genuinely strong. Don't inflate; account for hints and interviewer help.

Criteria keys: understand_code, use_ai, testing, problem_solving, communication, collaboration, clarifying_questions, introduction,
resume_depth, past_problem, deep_dive, feature_design, candidate_questions.

<scores>
{"verdict": "strong no hire|no hire|lean no hire|lean hire|hire|strong hire",
 "verdict_reason": "2-3 sentences, the way a Bloomberg interviewer would write it in the hiring packet",
 "scores": {"understand_code": {"score": 2, "evidence": "one or two sentences with timestamps"}, "...": {}},
 "overall": {"score_sum": 0, "max": 0, "percent": 0},
 "bugs": {"total": 5, "found": 0, "fixed": 0, "tested": 0,
          "details": [{"id": "B1", "name": "...", "status": "fixed|found|missed|told by interviewer", "when": "mm:ss or null", "note": "..."}]},
 "clarifying_questions": {"asked": ["..."], "missed": ["the important PM-table questions they never asked"]},
 "hints": {"count": 0, "levels": [], "help_received": ["mm:ss what the interviewer supplied"]},
 "time_to_first_test": "mm:ss or null",
 "ai_usage": "one sentence",
 "strengths": ["3-5 specific strengths"],
 "weaknesses": ["3-5 specific weaknesses"],
 "action_items": ["the 3 most important things to change next time, each actionable"],
 "next_exercise": "e.g. r1/15 because ...",
 "spoken_summary": "5-7 sentences to be read aloud to the candidate: verdict, the score, the biggest strength, the two biggest fixes, warm and direct"}
</scores>

overall.score_sum is the sum of non-null scores, max is 4 × the number of non-null scores, percent is round(100 × sum / max).
