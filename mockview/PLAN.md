# mockview — Build Plan

A voice-driven mock interviewer for the Bloomberg AI-assisted coding rounds. It runs on this laptop, uses the Claude subscription
through Claude Code (no API key), and turns the exercises in `interview-prep/` into a realistic 60-minute interview followed by a
detailed debrief.

---

## 1. Goals

1. **Feel like a real interview.** A named Bloomberg software engineer (fictional persona) greets you, explains the format, asks
   you to introduce yourself, digs into your resume, asks about a hard problem you solved, runs a coding exercise, asks follow-up
   questions about your fixes, gives a feature request, takes your questions, and closes.
2. **Voice both ways**, hands-free, with low enough latency to feel conversational.
3. **Sees your work**: screenshots of your screen (Zed + its agent panel) and the session's git diff and test results.
4. **Never leaks answers** to you or to your coding agent.
5. **Debrief after every interview**: evidence-based scores per criterion, strengths, weaknesses, missed opportunities, better
   answers, an action plan, and progress tracking across sessions.

### Non-goals
- Interrupting you mid-sentence (turn-based by design).
- Running on the NVIDIA GPU (CPU only; GPU support stays an optional build feature, off by default).
- Replacing `mock.py`; mockview drives it.

---

## 2. Environment (checked 2026-10-20)

| Item | Status |
|---|---|
| CPU / RAM | Intel i9-11950H, 16 threads, AVX2; 31 GB RAM |
| GPU | RTX A2000 (not used) |
| Rust | rustc / cargo 1.98.1, rustup 1.29.1 |
| C toolchain | clang 22, gcc 16, pkg-config — **cmake missing** |
| Audio | PipeWire 1.6.8 (Pulse compatible); mic `alsa_input…analog-stereo`; output Bluetooth headphones |
| Display | Hyprland, eDP-1 3840×2400 @ scale 2; `grim`, `slurp`, `hyprctl` present |
| Tools | poppler (`pdftotext`), ffmpeg, git, Python 3.14 |
| Editor | Zed 1.18.1 (`zeditor`) |
| Claude Code | 2.1.287 — supports `-p`, `--input-format stream-json`, `--output-format stream-json`, `--include-partial-messages`, `--resume`, `--session-id`, `--system-prompt-file`, `--tools`, `--allowed-tools`, `--add-dir`, `--permission-mode`, `--settings`, `--strict-mcp-config` |

### To install / download
| What | Why | Size |
|---|---|---|
| `cmake` (pacman) | build whisper.cpp via `whisper-rs` | small |
| `espeak-ng` (pacman) | phonemes for Kokoro (and Piper fallback) | small |
| whisper `ggml-large-v3-turbo-q5_0.bin` | speech-to-text | ~550 MB |
| whisper `ggml-small.en.bin` | faster fallback model | ~470 MB |
| Kokoro v1.0 ONNX + voices | interviewer voice | ~330 MB |
| Silero VAD v5 ONNX | end-of-speech detection | ~2 MB |
| ONNX Runtime | fetched automatically by the `ort` crate at build time (CPU build) | ~20 MB |

Models live in `~/.local/share/mockview/models/` (not in the repo).

---

## 3. Architecture

```
┌────────────────────────── mockview (one Rust binary, tokio) ──────────────────────────┐
│                                                                                        │
│  mic (cpal, 16 kHz mono) ─► Silero VAD ─► utterance ─► whisper (large-v3-turbo) ─► text │
│                                                                    │                   │
│                       ┌────────────── Orchestrator ◄───────────────┘                   │
│                       │  interview state machine + timer + check-in scheduler          │
│                       │  observation: grim screenshot, git diff, test runs             │
│                       ▼                                                                │
│        Claude Code process (claude -p, stream-json in/out, persistent session)         │
│                       │  streamed text, sentence by sentence                           │
│                       ▼                                                                │
│        Kokoro TTS (ONNX) ─► audio out (cpal) ─► headphones   [mic gated while speaking]│
│                                                                                        │
│  ratatui TUI: timer · phase · live transcript · status · keys                          │
│  run recorder: transcript.jsonl · timeline.json · screenshots/ · diff.patch · grade    │
└────────────────────────────────────────────────────────────────────────────────────────┘
          │ starts session via mock.py, opens it in Zed, places windows (hyprctl)
          ▼
   Zed on sessions/<id>/  +  Zed agent panel (Claude Code via ACP)  ← candidate side
```

After the interview: a **separate** Claude Code call (evaluator role) reads the run folder and writes the debrief.

### Crate layout (Cargo workspace)

```
mockview/
├── Cargo.toml                 workspace
├── crates/
│   ├── mv-audio/              cpal capture/playback, resampling (rubato), ring buffers, mic gating
│   ├── mv-vad/                Silero VAD via ort, endpointing state machine
│   ├── mv-stt/                whisper-rs wrapper, prompt biasing, model selection
│   ├── mv-tts/                Kokoro via ort + espeak-ng phonemes; Piper fallback; sentence queue
│   ├── mv-claude/             Claude Code process manager: stream-json protocol, images, retries
│   ├── mv-interview/          state machine, persona, prompts, hint ladder, check-in policy
│   ├── mv-observe/            screenshots (grim + downscale), git diff/stat, test runner, mock.py bridge
│   ├── mv-record/             run folder, transcript/timeline writers
│   ├── mv-debrief/            evaluator prompt, scores.json schema, markdown report, progress
│   └── mv-tui/                ratatui interface
├── src/main.rs                CLI (clap)
├── prompts/                   interviewer.md, evaluator.md, persona-pool.toml (editable, not compiled in)
├── resume/                    put resume.pdf or resume.md here (git-ignored)
├── runs/                      one folder per interview (git-ignored)
└── mockview.toml              config
```

### Key crates
`tokio`, `clap`, `serde`/`serde_json`, `toml`, `anyhow`/`thiserror`, `tracing`, `cpal`, `rubato`, `ringbuf`, `ort`
(download-binaries, CPU), `whisper-rs`, `ndarray`, `ratatui` + `crossterm`, `image` (screenshot downscale), `chrono`,
`uuid`, `regex`, `rand`.

---

## 4. Components in detail

### 4.1 Audio (`mv-audio`)
- Capture from the default PipeWire source via cpal at the device rate; resample to **16 kHz mono f32** (rubato).
- Playback to the default sink (Bluetooth headphones) at Kokoro's 24 kHz, resampled as needed.
- **Mic gating:** capture is ignored while the interviewer is speaking plus 300 ms tail, so its voice never becomes your input
  (also protects against speakers if headphones are off).
- Keys: `Space` = push-to-talk override, `m` = mute mic, `s` = stop the interviewer speaking.

### 4.2 Voice activity detection (`mv-vad`)
- Silero VAD v5 on 32 ms frames.
- **Endpointing:** an utterance ends after **900 ms** of silence (configurable). Short pauses while thinking don't end your turn;
  holding `Space` disables endpointing for long answers.
- Pre-roll of 300 ms so the first syllable isn't clipped. Utterances under 400 ms of speech are discarded (coughs, clicks).

### 4.3 Speech-to-text (`mv-stt`)
- `whisper-rs` with `ggml-large-v3-turbo-q5_0`, English, greedy/beam 1, 8 threads, CPU only.
- **Prompt biasing:** whisper's initial prompt is filled with technical vocabulary (deque, heap, idempotency, O(log n), bisect,
  unittest, Decimal, …) plus identifiers from the current exercise (file names, function names, spec terms such as "rollover",
  "haircut") and names from your resume. This is the single biggest accuracy win for interview speech.
- Expected: ~2–4 s for a 15 s answer. `small.en` selectable in config if that feels slow.

### 4.4 Text-to-speech (`mv-tts`)
- Kokoro v1.0 (ONNX, CPU) with one fixed voice per persona (e.g. `am_michael`, `af_heart`, `bm_george`); speed 1.0.
- **Streaming:** Claude's reply arrives token by token (`--include-partial-messages`); text is split into sentences and each
  sentence is synthesised and queued as soon as it's complete, so the interviewer starts speaking ~1 s after the first sentence
  instead of after the whole reply.
- Text cleanup before speaking: strip markdown, expand `O(n log n)` → "O of n log n", read code identifiers naturally.
- Fallback: Piper (`en_US-ryan-high`) if Kokoro fails to load.

### 4.5 Claude integration (`mv-claude`)
- One long-lived process per interview:
  ```
  claude -p --input-format stream-json --output-format stream-json --include-partial-messages
         --session-id <uuid> --system-prompt-file <run>/interviewer-prompt.md
         --tools Read,Glob,Grep --permission-mode default
         --add-dir <exercise notes dir> --add-dir <session dir> --add-dir <run dir>
         --strict-mcp-config --settings <minimal settings: no hooks, no MCP>
         --model <config, default: current best>
  ```
- **Read-only:** no Bash, Write or Edit. mockview itself takes screenshots, runs tests and collects diffs, and passes the results in.
- Each turn is a user message containing: what you said, elapsed time and current phase, and (when relevant) a fresh screenshot
  as an image block plus a short diff summary.
- **Phase 0 verifies** that stream-json input accepts image blocks and that headless mode works with the subscription login; if
  images aren't accepted, screenshots are saved to the run folder and the interviewer reads them with its Read tool instead.
- Crash handling: if the process dies, restart with `--resume <session-id>`; the conversation continues.
- Usage control: screenshots downscaled to ~1600 px wide (PNG→JPEG q80), sent only at check-ins or when you mention the screen.

### 4.6 Observation (`mv-observe`)
- `grim -o eDP-1` (or the monitor with Zed focused, via `hyprctl activewindow`) → downscale → `runs/<id>/screenshots/HHMMSS.jpg`.
- `git -C <session> diff --stat` and full diff (truncated to ~8 KB) since the last check-in.
- Test runs: `python -m unittest discover -s tests` in the session folder when the interviewer asks or at check-ins; result
  summary only (pass/fail counts, failing test names).
- Activity signal: file mtimes in the session folder → "idle for 6 minutes" style hints for the scheduler.

### 4.7 Interview orchestration (`mv-interview`)

#### Phases (60 minutes, configurable)

| Time | Phase | Interviewer behaviour |
|---|---|---|
| 0–2 | **Greeting** | Introduces self (persona name, team, years at Bloomberg), small talk, explains the format and that AI use is expected. |
| 2–8 | **Introduction & resume** | "Tell me about yourself." Then 2–3 follow-ups on resume items it chose before the call: decisions, trade-offs, numbers, your specific contribution. |
| 8–12 | **Past problem** | "Tell me about a hard technical problem you solved." Probes the root cause, how you verified the fix, what you'd do differently. |
| 12–15 | **Exercise setup** | Starts the session via `mock.py start`, opens Zed, asks you to read the spec and summarise it. |
| 15–45 | **Coding** | Plays the product manager (answers from the notes' PM table only). Check-ins. Hint ladder when stuck. Notes which bugs you find. |
| 45–55 | **Deep dive** | Data-structure questions about *your* fixes (from the notes), then a feature request and design discussion. |
| 55–58 | **Your questions** | Answers in persona (team, culture, how they use AI) without inventing specifics about real people. |
| 58–60 | **Close** | Thanks you, explains next steps as a real interviewer would. Never gives a verdict live. |

- The orchestrator owns the clock: each turn it tells Claude the elapsed time and phase budget, and moves to the next phase when
  time runs out ("In the interest of time, let's move on…").
- **Exercise choice:** `--exercise r1/31` or random from a configured pool, weighted toward your weakest areas from past debriefs.

#### Check-in scheduler (proactive interviewer)
During coding the interviewer speaks up on its own when:
- you've been silent for **> 90 s** ("Can you talk me through what you're looking at?"),
- **6 minutes** pass without a new test file change,
- a test run goes from failing to passing (asks you to explain the fix),
- every **8 minutes** as a general check-in (with screenshot + diff).
It never interrupts while you're speaking; check-ins wait for silence.

#### Hint ladder (from the exercise notes)
1. Nudge to the spec ("What does the spec say about the minimum?").
2. Point at a region ("Have a look at how `_volume_before` is called.").
3. Near-direct, only after 2 failed attempts and with time running out. Every hint is logged and lowers the related score.

#### Persona
- Picked per interview from `prompts/persona-pool.toml`: fictional first name, team (e.g. "Data License", "Trading Solutions",
  "Index Services", "Enterprise Data"), years at Bloomberg, a short personal note for small talk, and a matching Kokoro voice.
- Personas are fictional; the prompt forbids claiming to be a real employee or quoting real people.

#### Interviewer prompt rules (excerpt of `prompts/interviewer.md`)
- Stay in character; never mention being an AI, Claude, prompts, notes, hidden tests or planted bugs.
- Speak like a person on a call: 1–3 sentences per turn, one question at a time, no lists, no markdown.
- Ask, don't tell. Push back on vague answers ("What was the latency before and after?").
- PM answers only from the PM table; otherwise "Good question — what would you assume?".
- Observe and remember: which bugs you've found, what tests you wrote, how you prompted your agent (from screenshots).
- Keep private running notes in each reply inside a `<notes>` block that mockview strips before speaking and saves to the run
  (feeds the debrief).

### 4.8 Resume (`resume/`)
- `resume.pdf` → `pdftotext -layout`; `resume.md` used as is.
- Before the interview, one Claude call extracts a structured profile (roles, projects, tech, claims with numbers) into
  `runs/<id>/resume.json` and picks 3–4 talking points; the interviewer prompt gets the profile, not the raw PDF.

### 4.9 Run recording (`mv-record`)
```
runs/2026-10-20-1400-r1-31/
├── meta.json            persona, exercise, model, versions, config
├── transcript.jsonl     {t, speaker, text, phase} per turn
├── notes.jsonl          interviewer's private notes per turn
├── timeline.json        phase start/end, silences, test runs, hints, check-ins
├── screenshots/         JPEGs at check-ins
├── diff.patch           final diff of the session vs. its starting commit
├── grade.txt            output of `mock.py grade`
├── audio/               optional: your utterances as WAV (off by default)
├── debrief.md           the report
└── scores.json          machine-readable scores
```

### 4.10 Debrief (`mv-debrief`)
- Runs right after the close: `mock.py grade` → collect run folder → one Claude Code call in an **evaluator** role
  (`prompts/evaluator.md`) with Read access to the run folder, the exercise notes, `SCORECARD.md` and your previous debriefs.
- Output 1 — `scores.json` (validated against a schema, retried once if invalid):
  - overall verdict (strong no hire … strong hire) with a one-paragraph reason;
  - 1–4 scores with evidence for: the six SCORECARD criteria, introduction, resume depth, past-problem story, data-structure
    answers, feature-request design;
  - bugs found / fixed / tested (from hidden checks + transcript), hints used, time to first test, time per bug.
- Output 2 — `debrief.md`:
  1. Verdict
  2. Scorecard table with evidence (timestamped quotes, diff excerpts)
  3. What you did well
  4. What hurt you (moment → why → what a strong candidate does)
  5. Missed opportunities (bugs not found with the spec sentence that leads to them; PM questions not asked; resume points left shallow)
  6. Better answers: rewrites of your 2–3 weakest answers
  7. Action plan: 3 drills + the next exercise to do
  8. Progress vs. last sessions
- Optional 2-minute spoken summary at the end of the call.

### 4.11 Progress (`mockview progress`)
- Reads all `runs/*/scores.json`: per-criterion trend (sparklines in the terminal), recurring mistakes, action points
  followed or not, exercises done, suggestions for next.
- The next interview's prompt gets a short "known weaknesses" section so the interviewer probes them.

### 4.12 Terminal UI (`mv-tui`)
```
┌ mockview ─ R1-31 Meeting Calendar ─ Daniel (Index Services) ──────── 23:41 / 60:00 ┐
│ Phase: Coding (15–45)   ██████████████░░░░░░░░   next check-in 02:10                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ 23:05 Daniel  So what's your hypothesis for why Eve got Ana's meeting?              │
│ 23:20 You     I think the request id map isn't keyed by organizer…                  │
│ 23:31 Daniel  How would you prove that before changing anything?                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ ● listening   mic ▁▃▅▂   STT large-v3-turbo   voice am_michael   Claude ✓          │
│ [space] hold to talk  [m] mute  [s] stop voice  [n] next phase  [q] end interview   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 4.13 Zed and window layout
- After `mock.py start`, run `zeditor <session dir>`.
- Optional `layout = "side"`: `hyprctl dispatch` moves mockview to a narrow column on the right and Zed to the rest.
- Reminder at session start: in Zed's agent panel, decline any read outside the session folder.

### 4.14 CLI
```
mockview check                 verify mic, speakers, models, claude login, grim, zeditor
mockview interview [--exercise r1/31] [--minutes 60] [--text] [--persona NAME]
mockview debrief <run>         (re)generate the report for a run
mockview progress              trends across runs
mockview say "text"            test the voice
mockview listen                test mic + VAD + STT (prints transcripts)
mockview models download       fetch models with checksums
```
`--text` runs the whole interview by typing instead of voice (useful for testing and noisy places).

### 4.15 Configuration (`mockview.toml`)
```toml
[interview]  minutes = 60  exercise_pool = ["round-1/*"]  check_in_minutes = 8  silence_prompt_s = 90
[audio]      input = "default"  output = "default"  endpoint_silence_ms = 900  record_audio = false
[stt]        model = "large-v3-turbo-q5_0"  threads = 8
[tts]        engine = "kokoro"  speed = 1.0
[claude]     model = "default"  screenshot_width = 1600
[paths]      kit = "~/Projects/interview-prep"  models = "~/.local/share/mockview/models"
[layout]     mode = "side"
```

---

## 5. Latency budget (per turn, target ≤ 4 s to first spoken word)

| Step | Target |
|---|---|
| End-of-speech detection | 0.9 s |
| Whisper large-v3-turbo (15 s utterance) | 2–3 s |
| Claude to first sentence (streamed) | 1–2 s |
| Kokoro first sentence | 0.3–0.6 s |
| **Total** | **~4–6 s** worst case; `small.en` brings it to ~3 s |

Measured in phase 2 and phase 5; if it's over, options are: smaller STT model, shorter endpointing, a short spoken filler
("Mm, okay —") played immediately while Claude thinks.

---

## 6. Safety rules for the kit

- The candidate's agent (Zed) only ever sees `sessions/<id>/`.
- The interviewer has read-only access to that exercise's notes, the session, the run folder and the resume — nothing else.
- Resume and runs are git-ignored; nothing is uploaded except what Claude Code sends to Anthropic as part of the conversation.

---

## 7. Build phases

Each phase ends with a check you can run.

| # | Phase | Deliverable | Done when |
|---|---|---|---|
| 0 | **Spikes** | Prove the risky bits: stream-json multi-turn session with the subscription; image blocks in stream-json; Kokoro + espeak-ng in Rust; whisper-rs build with cmake. | Four tiny binaries succeed. |
| 1 | **Skeleton** | Workspace, config, CLI, `check`, model download with checksums, tracing logs. | `mockview check` all green. |
| 2 | **Ears** | Capture → VAD → whisper; `mockview listen`. | Transcribes 10 technical sentences with ≥ 95% word accuracy; latency measured. |
| 3 | **Mouth** | Kokoro TTS, sentence streaming, text cleanup, mic gating; `mockview say`. | Speaks a 3-sentence reply starting < 1 s after the first sentence is ready; no self-capture. |
| 4 | **Brain** | Claude process manager, interviewer prompt, persona, `--text` interview of the greeting + resume phases. | A typed 10-minute conversation stays in character and asks resume follow-ups. |
| 5 | **Conversation** | Wire ears + brain + mouth; TUI; phase timer. | A spoken 10-minute intro + resume conversation feels natural. |
| 6 | **Exercise** | `mock.py` bridge, Zed launch, screenshots, diffs, tests, check-ins, hint ladder, PM role. | Full 60-minute dry run on R1-31 with check-ins firing. |
| 7 | **Debrief** | Evaluator prompt, schema, report, `progress`. | Debrief for the dry run cites timestamps, diff lines and hidden-check results. |
| 8 | **Polish** | Window layout, spoken summary, crash recovery (`--resume`), docs (`README.md`). | Kill Claude mid-interview → it recovers; README walkthrough works from scratch. |

Testing throughout: unit tests for the state machine, endpointing, text cleanup and schema validation; a fake Claude backend
that replays recorded stream-json; recorded WAV fixtures for STT regression.

---

## 8. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Headless mode or images behave differently than expected | Phase 0 spike; fallback to screenshots read via the Read tool. |
| Latency feels slow | Streaming TTS, filler phrases, `small.en`, shorter endpointing. |
| Whisper mishears jargon | Prompt biasing with exercise + resume vocabulary; `small.en` vs turbo comparison in phase 2. |
| Interviewer breaks character or leaks a bug | Strict prompt, `<notes>` channel for private thoughts, output filter for words like "planted", "hidden test", "B1". |
| Usage limits on Pro | Screenshots only at check-ins, downscaled; one persistent session (prompt caching); `--text` mode. |
| Bluetooth audio latency | Measured in `check`; output buffer tuned; wired headphones recommended if > 250 ms. |
| Kokoro/ONNX build issues | Piper fallback behind the same trait. |

---

## 9. Decisions still open

1. Persona voice gender/accent preferences (default: rotate).
2. Keep recordings of your own audio for self-review? (default: off)
3. Default model for the interviewer and evaluator (default: whatever Claude Code uses; configurable).
