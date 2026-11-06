# mockview

A spoken mock interviewer for the Bloomberg AI-assisted coding rounds. It runs on your laptop and uses your Claude plan through
Claude Code (no API key). A fictional Bloomberg engineer interviews you for 60 minutes:
- greeting;
- your introduction and resume;
- a hard problem you solved;
- a coding exercise, done in Zed with your AI assistant;
- data-structure questions and a feature request;
- your questions, then the close.

Afterwards you get a detailed written debrief, and progress is tracked across interviews.

The interviewer assesses; it doesn't coach. It won't name or confirm bugs, suggest strategies or fill gaps in your spec summary.
Hints are rationed by mockview itself: only during coding, not in its first 5 minutes, at most one per 7 minutes, and never more
direct than "spend some time in the matching loop". Every hint counts against you in the debrief.

## Quick start

```bash
cd ~/Projects/interview-prep/mockview
./target/release/mockview check                       # everything green?
./target/release/mockview interview                   # a random pack you haven't done
./target/release/mockview interview --exercise r1/halcyon  # a specific one (r2/harbor for Round 2)
./target/release/mockview progress                    # scores and trends
```

Put your resume in `resume/` as `resume.pdf` or `resume.md` first; the interviewer asks about it.

Use headphones. The mic is ignored while the interviewer speaks, but headphones make it reliable.

## Exercises

By default the exercises are your **bloomberg-practice packs** (`~/Projects/bloomberg-practice`: 10 Round 1 and 10 Round 2 packs),
in Python only. Set `[paths] kit = "~/Projects/interview-prep"` to use the 100-exercise mock.py kit instead.

The packs ship with no tests and no answer key, so mockview handles both:
- **The interviewer's answer key.** Before a pack's first interview, mockview has Claude write one: the planted bugs, decisive answers
  to the PM questions, hints, data-structure questions and feature requests, minimal fixes and hidden tests. mockview then checks it
  itself: every hidden test must fail on the shipped code and pass once the fixes are applied, or the key is rewritten. This takes
  about a minute per pack. `mockview keys` writes all of them up front; `mockview exercises` shows which are ready. Keys are kept in
  `~/.local/share/mockview/keys/`, outside the pack repository, so they can't be pushed by accident. A key is rewritten automatically
  if the pack's code changes.
- **Your session.** Each interview copies the pack's committed version (your own uncommitted practice edits, like in quasar, are
  never included) to `bloomberg-practice/practice/mock-<date>-<pack>/`, which the repository already ignores. You get the README,
  brief, setup notes, tickets and `python/`. You don't get the C++ and Java ports, `PROJECT_MANAGER_NOTES.md` (you're expected to
  come up with the clarifying questions yourself; the debrief lists the ones you missed) or `SELF_REVIEW_AFTER.md`.
- **Tests.** You write pytest files as `python/test_*.py`. The session has a `.venv` with pytest that Zed's terminal picks up, so run
  `cd python && pytest -q`. The interviewer sees your test results and changed files as you go.
- **Round 2** packs: the interviewer tells you which ticket to start with.

## During the interview

| Key | Action |
|---|---|
| (just talk) | Your turn ends after a pause of 1.3 s (`endpoint_silence_ms`) |
| `space` | Keep the mic open through long pauses; press again to finish your answer |
| `m` | Mute or unmute your mic |
| `s` | Stop the interviewer talking |
| `l` | Ask the interviewer to look at your screen now |
| `n` | Skip to the next phase |
| `q` | End the interview (asks to confirm) |

When the coding phase starts, the session folder opens in Zed. Use Zed's agent panel as your AI assistant.
- **Only work in the session folder.** If the agent asks to read anything outside it, say no: the interviewer notes are in the kit.
- **The interviewer can see your work:** screenshots at check-ins, and your test results and changed files on every turn.

## After the interview

Your scores are printed in the terminal (verdict, overall percentage, a 1–4 score for each of 13 criteria, top 3 things to change).
The full debrief opens in Zed; it takes about 4 minutes and has six sections:

1. **Verdict and scorecard:** how a hiring panel would read it, every score with evidence, what a 4 would have looked like, and the
   help you received.
2. **The exercise, solved:**
   - the spec as testable rules, and every clarifying question you should have asked (with the product manager's answers);
   - a 30-minute plan with the exact prompts for your AI assistant;
   - for each planted bug: the spec sentence, how to find it, the test (full code), the minimal fix, and when you could have caught it.
3. **Minute by minute:** each phase and check-in, compared with what a strong candidate does at that point.
4. **Talking about yourself:** critiques and model answers built from your resume (introduction, resume follow-ups, hard problem),
   plus model answers to every data-structure question and feature request for the exercise.
5. **AI assistant and communication:** how you used the agent, a prompt playbook, and how to think out loud.
6. **Improvement plan:** top 3 priorities, a 7-day drill plan, a checklist for your next mock, and the next exercises.

`runs/<date>-<exercise>/` contains:

| File | What it is |
|---|---|
| `debrief.md` | The full written feedback |
| `scores.json` | Machine-readable scores |
| `transcript.txt` | Everything said, with timestamps |
| `diff.patch` | Your final code changes |
| `grade.txt` | Your test results and the hidden checks for each planted bug |
| `notes.jsonl` | The interviewer's private notes |
| `screenshots/` | Screenshots taken at check-ins |

`mockview debrief <run>` rewrites a debrief, and `mockview progress` shows trends, recurring weaknesses and your current action items.
The next interviewer quietly probes the weaknesses from your last debriefs.

## Other commands

| Command | Use |
|---|---|
| `mockview listen` | Test your mic and speech recognition live |
| `mockview say "Hello, I'm Daniel"` | Test the voice (`--voice bf_emma`, `--out file.wav`) |
| `mockview interview --text` | The whole interview by typing (no audio) |
| `mockview interview --minutes 30` | A shorter interview; phases scale |
| `mockview exercises`, `mockview personas` | What's available (and which packs have an answer key) |
| `mockview keys` | Write the answer keys for every pack now (`--exercise r2/harbor` for one, `--force` to rewrite) |

## Settings (`mockview.toml`)

- **`[stt] model`:** `auto` uses whisper `large-v3-turbo` (8-bit), the most accurate model for accents and technical words. Speech is
  transcribed in pieces while you talk, so little is left to process when you stop. Whisper's retry-on-garbage safety net is on, and
  repetition loops are collapsed.
- **`[paths] kit`:** where the exercises come from (see Exercises).
- **`[interview]`:** length, exercise pool (`round-1`, `round-2`, or one pack such as `round-2/harbor`), and how often the interviewer
  checks in.
- **`[claude] model`:** empty uses Claude Code's default. `screenshots = false` stops screenshots being sent.
- **`[editor] command`:** `zeditor` by default; `none` to open the folder yourself.
- **`[tts] voice`:** `auto` uses the persona's voice. Personas are in `prompts/personas.toml`; the interviewer's behaviour is in
  `prompts/interviewer.md` and the feedback rules in `prompts/debrief/` (one file per report section). All are plain text you can edit.

## Privacy

Everything runs locally except the Claude conversation. That sends the transcript, your resume text, the exercise, and screenshots of
your screen at check-ins (when `screenshots = true`). Your resume and runs are git-ignored.

## Building

```bash
sudo pacman -S --needed cmake espeak-ng   # once
cargo build --release
```

Models live in `~/.local/share/mockview/models/` (whisper large-v3-turbo and small.en, Kokoro v1.0, Silero VAD).
