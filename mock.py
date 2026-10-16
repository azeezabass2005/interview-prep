#!/usr/bin/env python3
"""Mock-interview runner for the Bloomberg AI-assisted coding rounds.

  python mock.py list                     list every exercise
  python mock.py start 1                  random round-1 exercise in a fresh session folder
  python mock.py start 2 07               a specific round-2 exercise
  python mock.py grade <session-dir>      run visible + hidden tests, show your diff stats
  python mock.py pm <session-dir>         "ask the interviewer": PM answers to clarifying questions only (round 1)
  python mock.py notes <session-dir>      print the full interviewer notes (after you finish!)
  python mock.py verify                   maintainer self-check of every exercise

Open ONLY the session folder in your IDE/agent. Never open the repo root, or the agent
can read interviewer-notes/.
"""
import datetime
import importlib.util
import os
import random
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
ROUNDS = {"1": "round-1", "2": "round-2"}
NOTES = os.path.join(ROOT, "interviewer-notes")
SESSIONS = os.path.join(ROOT, "sessions")
TIMEBOX = {"1": 50, "2": 50}


def exercises(rnd):
    base = os.path.join(ROOT, ROUNDS[rnd])
    return sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))


def find(rnd, key):
    matches = [e for e in exercises(rnd) if e.startswith(key.zfill(2)) or key in e]
    if len(matches) != 1:
        sys.exit(f"no unique round-{rnd} exercise matches {key!r}: {matches}")
    return matches[0]


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def cmd_list():
    for rnd in ROUNDS:
        print(f"\nRound {rnd} ({ROUNDS[rnd]})")
        for e in exercises(rnd):
            print("  ", e)


def cmd_start(rnd, key=None):
    name = find(rnd, key) if key else random.choice(exercises(rnd))
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    dest = os.path.join(SESSIONS, f"{stamp}-r{rnd}-{name}")
    shutil.copytree(os.path.join(ROOT, ROUNDS[rnd], name), dest,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.db"))
    with open(os.path.join(dest, ".mock-session"), "w") as f:
        f.write(f"round={rnd}\nexercise={name}\nstarted={datetime.datetime.now().isoformat()}\n")
    with open(os.path.join(dest, ".gitignore"), "w") as f:
        f.write("__pycache__/\n*.pyc\n*.db\n.mock-session\n")
    git(dest, "init", "-q")
    git(dest, "add", "-A")
    git(dest, "-c", "user.name=mock", "-c", "user.email=mock@local", "commit", "-qm", "starting point")
    brief = "SPEC.md" if rnd == "1" else "README.md and tickets/"
    print(f"""
Session ready: {dest}

  1. Open ONLY this folder in your IDE and agent.
  2. Spend 5 minutes on your resume and a past problem you solved (out loud).
  3. Read {brief}. Timebox: {TIMEBOX[rnd]} minutes. Narrate everything.
  4. When done:  python {os.path.relpath(__file__)} grade "{dest}"
""")


def run_in_subprocess(cwd, pattern="test*.py"):
    proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", pattern, "-v"],
                          cwd=cwd, capture_output=True, text=True)
    return proc.returncode, proc.stderr


def session_meta(session):
    meta = {}
    path = os.path.join(session, ".mock-session")
    if not os.path.exists(path):
        sys.exit(f"{session} is not a mock session folder")
    for line in open(path):
        k, _, v = line.strip().partition("=")
        meta[k] = v
    return meta


def notes_dir(meta):
    return os.path.join(NOTES, ROUNDS[meta["round"]], meta["exercise"])


def cmd_grade(session):
    session = os.path.abspath(session)
    meta = session_meta(session)
    started = datetime.datetime.fromisoformat(meta["started"])
    mins = (datetime.datetime.now() - started).total_seconds() / 60
    print(f"Exercise: round {meta['round']} / {meta['exercise']}   elapsed: {mins:.0f} min\n")

    code, out = run_in_subprocess(session)
    print("== Your test suite ==")
    print("\n".join(l for l in out.splitlines() if l.startswith(("Ran", "OK", "FAILED"))))

    hidden = os.path.join(notes_dir(meta), "hidden_tests.py")
    target = os.path.join(session, "tests", "test_zz_hidden_grading.py")
    shutil.copy(hidden, target)
    try:
        code, out = run_in_subprocess(session, pattern="test_zz_hidden_grading.py")
    finally:
        os.remove(target)
    print("\n== Hidden checks (one per planted issue) ==")
    for line in out.splitlines():
        if " ... " in line:
            name, _, status = line.partition(" ... ")
            mark = "PASS" if status.strip() == "ok" else "----"
            print(f"  [{mark}] {name.split(' ')[0]}")
    print("\n== Your diff ==")
    print(git(session, "add", "-A").stdout + git(session, "diff", "--cached", "--stat", "HEAD").stdout)
    git(session, "reset", "-q")
    print("Next: review the diff out loud, then read the notes:")
    print(f'  python {os.path.relpath(__file__)} notes "{session}"')
    print("Score yourself with SCORECARD.md. Hidden checks are a guide; reasoning is the grade.")


def cmd_notes(session):
    meta = session_meta(os.path.abspath(session))
    for name in sorted(os.listdir(notes_dir(meta))):
        if name.endswith(".md"):
            print(open(os.path.join(notes_dir(meta), name)).read())


def cmd_pm(session):
    meta = session_meta(os.path.abspath(session))
    text = open(os.path.join(notes_dir(meta), "NOTES.md")).read()
    sections = text.split("\n## ")
    pm = [sec for sec in sections if "PM" in sec.splitlines()[0]]
    if not pm:
        print("No PM sheet for this exercise: round 2 tickets and the README are the spec.\n"
              "Say your question out loud, state your assumption, and write a test that makes it explicit.")
        return
    print("## " + pm[0].strip())


def load_fixes(path):
    spec = importlib.util.spec_from_file_location("fixes", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.FIXES


def apply_fixes(workdir, fixes):
    for rel, old, new in fixes:
        path = os.path.join(workdir, rel)
        text = open(path).read()
        if text.count(old) != 1:
            raise AssertionError(f"{rel}: fix anchor found {text.count(old)} times: {old[:60]!r}")
        open(path, "w").write(text.replace(old, new))


def hidden_results(workdir, hidden):
    shutil.copy(hidden, os.path.join(workdir, "tests", "test_zz_hidden_grading.py"))
    proc = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests",
                           "-p", "test_zz_hidden_grading.py", "-v"],
                          cwd=workdir, capture_output=True, text=True)
    os.remove(os.path.join(workdir, "tests", "test_zz_hidden_grading.py"))
    statuses = {}
    for line in proc.stderr.splitlines():
        if " ... " in line:
            name, _, status = line.partition(" ... ")
            statuses[name.split(" ")[0]] = status.strip()
    return statuses, proc.stderr


def verify_one(rnd, name):
    src = os.path.join(ROOT, ROUNDS[rnd], name)
    nd = os.path.join(NOTES, ROUNDS[rnd], name)
    problems = []
    for required in ("NOTES.md", "hidden_tests.py", "fixes.py"):
        if not os.path.exists(os.path.join(nd, required)):
            return [f"missing {required}"]
    with tempfile.TemporaryDirectory() as tmp:
        work = os.path.join(tmp, name)
        shutil.copytree(src, work, ignore=shutil.ignore_patterns("__pycache__", "*.db"))
        code, out = run_in_subprocess(work)
        if code != 0:
            problems.append("visible tests fail on buggy code:\n" + out[-1500:])
        before, raw = hidden_results(work, os.path.join(nd, "hidden_tests.py"))
        if not before:
            problems.append("hidden tests did not load:\n" + raw[-1500:])
        passing = [n for n, s in before.items() if s == "ok"]
        if passing:
            problems.append(f"hidden tests already pass on buggy code: {passing}")
        if "ImportError" in raw or "ModuleNotFoundError" in raw or "SyntaxError" in raw:
            problems.append("hidden tests have import/syntax errors:\n" + raw[-1500:])
        try:
            apply_fixes(work, load_fixes(os.path.join(nd, "fixes.py")))
        except AssertionError as e:
            return problems + [str(e)]
        code, out = run_in_subprocess(work)
        if code != 0:
            problems.append("visible tests fail after fixes:\n" + out[-1500:])
        after, raw = hidden_results(work, os.path.join(nd, "hidden_tests.py"))
        failing = [n for n, s in after.items() if s != "ok"]
        if failing:
            problems.append(f"hidden tests still fail after fixes: {failing}\n" + raw[-2500:])
        return problems + ([] if problems else [f"ok ({len(before)} hidden checks)"])


def cmd_verify(only=None):
    bad = 0
    for rnd in ROUNDS:
        for name in exercises(rnd):
            if only and only not in name:
                continue
            result = verify_one(rnd, name)
            ok = len(result) == 1 and result[0].startswith("ok")
            bad += not ok
            print(f"[{'OK ' if ok else 'BAD'}] r{rnd} {name}: " + "\n".join(result))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
    elif args[0] == "list":
        cmd_list()
    elif args[0] == "start" and len(args) >= 2:
        cmd_start(args[1], args[2] if len(args) > 2 else None)
    elif args[0] == "grade" and len(args) == 2:
        cmd_grade(args[1])
    elif args[0] == "pm" and len(args) == 2:
        cmd_pm(args[1])
    elif args[0] == "notes" and len(args) == 2:
        cmd_notes(args[1])
    elif args[0] == "verify":
        cmd_verify(args[1] if len(args) > 1 else None)
    else:
        print(__doc__)
