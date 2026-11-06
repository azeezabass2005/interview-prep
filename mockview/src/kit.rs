use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::SystemTime;

use anyhow::{anyhow, bail, Context, Result};
use rand::seq::IndexedRandom;

#[derive(Debug, Clone)]
pub struct Exercise {
    pub round: u8,
    pub name: String,
    pub dir: PathBuf,
    pub notes_dir: PathBuf,
    /// A bloomberg-practice style pack (python/ cpp/ java/, no tests, no answer key) rather than a mock.py kit exercise.
    pub pack: bool,
}

/// True for a kit run by mock.py (exercises with tests and interviewer notes); false for a folder of practice packs.
pub fn is_mock_kit(kit: &Path) -> bool {
    kit.join("mock.py").exists()
}

/// Where generated answer keys for practice packs live (outside the pack repository, so they're never shared by accident).
pub fn keys_dir(kit: &Path) -> PathBuf {
    let name = kit.file_name().map(|n| n.to_string_lossy().to_string()).unwrap_or_else(|| "kit".into());
    dirs::data_dir().unwrap_or_else(|| PathBuf::from(".")).join("mockview/keys").join(name)
}

impl Exercise {
    pub fn new(kit: &Path, round: u8, name: &str) -> Self {
        let round_name = format!("round-{round}");
        let pack = !is_mock_kit(kit);
        let notes_dir = if pack { keys_dir(kit).join(&round_name).join(name) } else { kit.join("interviewer-notes").join(&round_name).join(name) };
        Self { round, name: name.into(), dir: kit.join(&round_name).join(name), notes_dir, pack }
    }

    pub fn id(&self) -> String {
        format!("r{}-{}", self.round, self.name)
    }

    pub fn title(&self) -> String {
        if self.pack {
            let readme = std::fs::read_to_string(self.dir.join("README.md")).unwrap_or_default();
            let first = readme.lines().next().unwrap_or("").trim_start_matches('#').trim();
            let title = first.rsplit(" - ").next().unwrap_or(first).trim();
            return if title.is_empty() { self.name.clone() } else { title.to_string() };
        }
        let notes = self.notes();
        notes
            .lines()
            .next()
            .map(|l| l.trim_start_matches('#').trim().split(':').next().unwrap_or("").trim().to_string())
            .filter(|t| !t.is_empty())
            .unwrap_or_else(|| self.name.clone())
    }

    pub fn spec(&self) -> String {
        if self.pack {
            let kit = self.dir.parent().and_then(Path::parent).unwrap_or(&self.dir);
            return pack_session_files(kit, &self.dir)
                .unwrap_or_default()
                .into_iter()
                .filter(|(p, _)| p.extension().is_some_and(|e| e == "md"))
                .map(|(p, bytes)| format!("### {}\n\n{}", p.display(), String::from_utf8_lossy(&bytes).trim()))
                .collect::<Vec<_>>()
                .join("\n\n");
        }
        let spec = self.dir.join("SPEC.md");
        if spec.exists() {
            return std::fs::read_to_string(spec).unwrap_or_default();
        }
        let mut text = std::fs::read_to_string(self.dir.join("README.md")).unwrap_or_default();
        if let Ok(entries) = std::fs::read_dir(self.dir.join("tickets")) {
            let mut files: Vec<_> = entries.flatten().map(|e| e.path()).collect();
            files.sort();
            for f in files {
                text.push_str("\n\n");
                text.push_str(&std::fs::read_to_string(f).unwrap_or_default());
            }
        }
        text
    }

    pub fn notes(&self) -> String {
        std::fs::read_to_string(self.notes_dir.join("NOTES.md")).unwrap_or_default()
    }

    pub fn is_ticket_style(&self) -> bool {
        if self.pack {
            return self.dir.join("tickets").is_dir();
        }
        !self.dir.join("SPEC.md").exists()
    }

    /// How the exercise is presented, for the interviewer prompt.
    pub fn format(&self) -> &'static str {
        match (self.pack, self.is_ticket_style()) {
            (false, true) => "README and tickets; they pick one ticket",
            (false, false) => "spec and codebase; find where the code doesn't match the spec",
            (true, false) => "a candidate brief with reported symptoms and a single-module Python service (python/). No tests are shipped: \
                they must reproduce each bug with a pytest test they write themselves, then fix it and keep their tests green. \
                They work in Python only; ignore the brief's mentions of C++ and Java",
            (true, true) => "a README, a tickets/ backlog and a multi-module Python service (python/). No tests are shipped: they \
                must reproduce each ticket's bug with a pytest test they write themselves, then fix it. Tell them which ticket to \
                start with (see 'Starting ticket' in your notes); they may move on to others. They work in Python only; ignore the \
                README's mentions of C++ and Java",
        }
    }

    /// The reference fix file in `notes_dir`, and the name it gets in a run folder.
    pub fn reference_fixes(&self) -> (PathBuf, &'static str) {
        if self.pack {
            (self.notes_dir.join("fixes.diff"), "reference-fixes.diff")
        } else {
            (self.notes_dir.join("fixes.py"), "reference-fixes.py")
        }
    }

    pub fn hidden_tests(&self) -> PathBuf {
        self.notes_dir.join(if self.pack { "test_hidden.py" } else { "hidden_tests.py" })
    }
}

fn walk(dir: &Path) -> Result<Vec<PathBuf>> {
    let mut out = Vec::new();
    for entry in std::fs::read_dir(dir)? {
        let p = entry?.path();
        if p.is_dir() {
            if p.file_name().is_some_and(|n| n == "__pycache__" || n == ".git" || n == ".venv" || n == ".pytest_cache") {
                continue;
            }
            out.extend(walk(&p)?);
        } else {
            out.push(p);
        }
    }
    Ok(out)
}

pub fn list(kit: &Path, pool: &[String]) -> Result<Vec<Exercise>> {
    let mut all = Vec::new();
    for round_dir in pool {
        let round_name = round_dir.split('/').next().unwrap_or(round_dir);
        let round: u8 = round_name.trim_start_matches("round-").parse().context("pool entries look like round-1")?;
        let filter = round_dir.split('/').nth(1).map(str::to_string);
        let base = kit.join(round_name);
        let mut names: Vec<String> = std::fs::read_dir(&base)
            .with_context(|| format!("reading {}", base.display()))?
            .flatten()
            .filter(|e| e.path().is_dir())
            .map(|e| e.file_name().to_string_lossy().to_string())
            .filter(|n| filter.as_ref().is_none_or(|f| f == "*" || n.starts_with(f.trim_end_matches('*'))))
            .collect();
        names.sort();
        for name in names {
            if name.starts_with('.') {
                continue;
            }
            all.push(Exercise::new(kit, round, &name));
        }
    }
    Ok(all)
}

pub fn resolve(kit: &Path, spec: &str) -> Result<Exercise> {
    let (round, key) = spec
        .trim_start_matches('r')
        .split_once(['/', '-'])
        .ok_or_else(|| anyhow!("exercise looks like r1/31 or r2/05"))?;
    let pool = vec![format!("round-{round}")];
    let matches: Vec<_> = list(kit, &pool)?
        .into_iter()
        .filter(|e| e.name.starts_with(&format!("{:0>2}", key)) || e.name.contains(key))
        .collect();
    match matches.len() {
        1 => Ok(matches.into_iter().next().unwrap()),
        0 => bail!("no exercise matches {spec}"),
        _ => bail!("{spec} is ambiguous: {:?}", matches.iter().map(|e| &e.name).collect::<Vec<_>>()),
    }
}

pub fn pick(kit: &Path, pool: &[String], done: &[String]) -> Result<Exercise> {
    let all = list(kit, pool)?;
    let fresh: Vec<_> = all.iter().filter(|e| !done.contains(&e.id())).cloned().collect();
    let choices = if fresh.is_empty() { all } else { fresh };
    choices.choose(&mut rand::rng()).cloned().ok_or_else(|| anyhow!("no exercises in pool {:?}", pool))
}

pub fn start_session(kit: &Path, ex: &Exercise) -> Result<PathBuf> {
    if ex.pack {
        return start_pack_session(kit, ex);
    }
    let num = ex.name.split('-').next().unwrap_or(&ex.name);
    let out = Command::new("python3")
        .arg("mock.py")
        .args(["start", &ex.round.to_string(), num])
        .current_dir(kit)
        .output()
        .context("running mock.py start")?;
    let text = String::from_utf8_lossy(&out.stdout);
    let line = text
        .lines()
        .find_map(|l| l.trim().strip_prefix("Session ready:"))
        .ok_or_else(|| anyhow!("mock.py start failed: {}{}", text, String::from_utf8_lossy(&out.stderr)))?;
    Ok(PathBuf::from(line.trim()))
}

pub fn grade(kit: &Path, ex: &Exercise, session: &Path) -> Result<String> {
    if ex.pack {
        return grade_pack(ex, session);
    }
    let out = Command::new("python3").arg("mock.py").arg("grade").arg(session).current_dir(kit).output()?;
    Ok(format!("{}{}", String::from_utf8_lossy(&out.stdout), String::from_utf8_lossy(&out.stderr)))
}

fn git(session: &Path, args: &[&str]) -> Result<String> {
    let out = Command::new("git").arg("-C").arg(session).args(args).output()?;
    Ok(String::from_utf8_lossy(&out.stdout).to_string())
}

pub fn diff(session: &Path) -> Result<String> {
    git(session, &["add", "-A"])?;
    let d = git(session, &["diff", "--cached", "--src-prefix=a/", "--dst-prefix=b/", "HEAD"])?;
    git(session, &["reset", "-q"])?;
    Ok(d)
}

pub fn diff_stat(session: &Path) -> Result<String> {
    git(session, &["add", "-A"])?;
    let d = git(session, &["diff", "--cached", "--stat", "HEAD"])?;
    git(session, &["reset", "-q"])?;
    Ok(d.trim().to_string())
}

#[derive(Debug, Clone, Default, PartialEq)]
pub struct TestRun {
    pub ran: u32,
    pub failed: u32,
    pub errors: u32,
    pub failing: Vec<String>,
}

impl TestRun {
    pub fn summary(&self) -> String {
        if self.ran == 0 {
            return "tests: none ran (or import error)".into();
        }
        let mut s = format!("tests: {} ran, {} failing, {} errors", self.ran, self.failed, self.errors);
        if !self.failing.is_empty() {
            s.push_str(&format!(" ({})", self.failing.join(", ")));
        }
        s
    }
}

pub fn run_tests(session: &Path) -> TestRun {
    if is_pack_session(session) {
        return match crate::pyenv::python() {
            Ok(py) => pytest(&py, &session.join("python"), &[]).0,
            Err(_) => TestRun::default(),
        };
    }
    let out = Command::new("python3")
        .args(["-m", "unittest", "discover", "-s", "tests", "-v"])
        .current_dir(session)
        .env("PYTHONDONTWRITEBYTECODE", "1")
        .output();
    let Ok(out) = out else { return TestRun::default() };
    parse_unittest(&String::from_utf8_lossy(&out.stderr))
}

pub fn parse_unittest(text: &str) -> TestRun {
    let mut run = TestRun::default();
    for line in text.lines() {
        if let Some(rest) = line.strip_prefix("Ran ") {
            run.ran = rest.split_whitespace().next().and_then(|n| n.parse().ok()).unwrap_or(0);
        }
        if let Some((name, status)) = line.split_once(" ... ") {
            let status = status.trim();
            if status == "FAIL" || status == "ERROR" {
                run.failing.push(name.split_whitespace().next().unwrap_or(name).to_string());
            }
        }
        if line.starts_with("FAILED (") {
            for part in line.trim_start_matches("FAILED (").trim_end_matches(')').split(", ") {
                if let Some(n) = part.strip_prefix("failures=") {
                    run.failed = n.parse().unwrap_or(0);
                }
                if let Some(n) = part.strip_prefix("errors=") {
                    run.errors = n.parse().unwrap_or(0);
                }
            }
        }
    }
    run
}

/// Latest change to a test file (test_*.py anywhere, or anything under tests/).
pub fn latest_test_mtime(session: &Path) -> Option<SystemTime> {
    walk(session)
        .ok()?
        .iter()
        .filter(|p| {
            let rel = p.strip_prefix(session).unwrap_or(p);
            rel.starts_with("tests") || p.file_name().is_some_and(|n| n.to_string_lossy().starts_with("test_"))
        })
        .filter_map(|p| p.metadata().ok()?.modified().ok())
        .max()
}

pub fn latest_mtime(dir: &Path) -> Option<SystemTime> {
    walk(dir).ok()?.iter().filter_map(|p| p.metadata().ok()?.modified().ok()).max()
}

pub fn focused_monitor() -> Option<String> {
    let out = Command::new("hyprctl").args(["monitors", "-j"]).output().ok()?;
    let v: serde_json::Value = serde_json::from_slice(&out.stdout).ok()?;
    v.as_array()?.iter().find(|m| m["focused"].as_bool() == Some(true))?["name"].as_str().map(str::to_string)
}

pub fn screenshot(dest: &Path, width: u32) -> Result<Vec<u8>> {
    let png = dest.with_extension("png");
    let mut cmd = Command::new("grim");
    if let Some(m) = focused_monitor() {
        cmd.args(["-o", &m]);
    }
    let status = cmd.arg(&png).status().context("running grim")?;
    if !status.success() {
        bail!("grim failed");
    }
    let status = Command::new("ffmpeg")
        .args(["-loglevel", "error", "-y", "-i"])
        .arg(&png)
        .args(["-vf", &format!("scale={width}:-1"), "-q:v", "4"])
        .arg(dest)
        .status()?;
    let _ = std::fs::remove_file(&png);
    if !status.success() {
        bail!("ffmpeg failed to downscale the screenshot");
    }
    Ok(std::fs::read(dest)?)
}

pub fn open_in_editor(command: &str, session: &Path) -> Result<()> {
    if command.is_empty() || command == "none" {
        return Ok(());
    }
    Command::new(command).arg(session).spawn().with_context(|| format!("starting {command}"))?;
    Ok(())
}

/// The pack's files as committed (so a candidate's uncommitted practice edits never leak into a mock), relative to the pack.
/// Falls back to the working tree, minus tests and caches, when the kit isn't a git repository.
pub fn pristine_files(kit: &Path, pack: &Path) -> Result<Vec<(PathBuf, Vec<u8>)>> {
    let rel = pack.strip_prefix(kit).unwrap_or(pack).to_string_lossy().replace('\\', "/");
    let listed = Command::new("git").arg("-C").arg(kit).args(["ls-tree", "-r", "-z", "--name-only", "HEAD", "--"]).arg(&rel).output();
    if let Some(out) = listed.ok().filter(|o| o.status.success() && !o.stdout.is_empty()) {
        let mut files = Vec::new();
        for path in String::from_utf8_lossy(&out.stdout).split('\0').filter(|p| !p.is_empty()) {
            let blob = Command::new("git").arg("-C").arg(kit).arg("show").arg(format!("HEAD:{path}")).output()?;
            if !blob.status.success() {
                bail!("git show HEAD:{path} failed");
            }
            let local = Path::new(path).strip_prefix(&rel).unwrap_or(Path::new(path)).to_path_buf();
            files.push((local, blob.stdout));
        }
        return Ok(files);
    }
    let mut files = Vec::new();
    for p in walk(pack)? {
        let name = p.file_name().map(|n| n.to_string_lossy().to_string()).unwrap_or_default();
        if name.starts_with("test_") || name == ".DS_Store" {
            continue;
        }
        files.push((p.strip_prefix(pack)?.to_path_buf(), std::fs::read(&p)?));
    }
    Ok(files)
}

/// What the candidate gets for a pack: the docs, tickets and the Python implementation. The C++ and Java ports, the PM
/// question list (they must come up with their own questions) and the after-exercise self review are left out.
pub fn pack_session_files(kit: &Path, pack: &Path) -> Result<Vec<(PathBuf, Vec<u8>)>> {
    let mut out = Vec::new();
    for (path, bytes) in pristine_files(kit, pack)? {
        let s = path.to_string_lossy().replace('\\', "/");
        let keep = s.starts_with("python/") || s.starts_with("tickets/") || matches!(s.as_str(), "README.md" | "CANDIDATE_BRIEF.md" | "SETUP.md");
        if !keep {
            continue;
        }
        let bytes = match s.as_str() {
            "SETUP.md" => python_only_setup(&String::from_utf8_lossy(&bytes)).into_bytes(),
            "README.md" | "CANDIDATE_BRIEF.md" => without_hidden_docs(&String::from_utf8_lossy(&bytes)).into_bytes(),
            _ => bytes,
        };
        out.push((path, bytes));
    }
    out.sort();
    Ok(out)
}

fn python_only_setup(text: &str) -> String {
    let cut = text.find("\n## C++").or_else(|| text.find("\n## Java")).unwrap_or(text.len());
    format!("{}\n", text[..cut].trim_end())
}

fn without_hidden_docs(text: &str) -> String {
    let aside = regex::Regex::new(r"\s*\(there is\s+a list to start from in `PROJECT_MANAGER_NOTES\.md`\)").unwrap();
    let text = aside.replace_all(text, "");
    let mut lines: Vec<&str> = text.lines().filter(|l| !l.contains("PROJECT_MANAGER_NOTES.md") && !l.contains("SELF_REVIEW_AFTER.md")).collect();
    let mut n = 0;
    let numbered = regex::Regex::new(r"^(\d+)\. ").unwrap();
    let renumbered: Vec<String> = lines
        .drain(..)
        .map(|l| match numbered.captures(l) {
            Some(c) => {
                n += 1;
                format!("{n}. {}", &l[c[0].len()..])
            }
            None => {
                if !l.trim().is_empty() {
                    n = 0;
                }
                l.to_string()
            }
        })
        .collect();
    format!("{}\n", renumbered.join("\n").trim_end())
}

pub fn is_pack_session(session: &Path) -> bool {
    session.join("python").join("conftest.py").exists() && !session.join("tests").exists()
}

fn write_files(dest: &Path, files: &[(PathBuf, Vec<u8>)]) -> Result<()> {
    for (rel, bytes) in files {
        let path = dest.join(rel);
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        std::fs::write(&path, bytes)?;
    }
    Ok(())
}

fn start_pack_session(kit: &Path, ex: &Exercise) -> Result<PathBuf> {
    let py = crate::pyenv::python()?;
    let stamp = chrono::Local::now().format("%Y-%m-%d-%H%M%S");
    let session = kit.join("practice").join(format!("mock-{stamp}-{}", ex.name));
    std::fs::create_dir_all(&session)?;
    write_files(&session, &pack_session_files(kit, &ex.dir)?)?;
    std::fs::write(session.join(".gitignore"), ".venv\n__pycache__/\n.pytest_cache/\n")?;
    let ok = |args: &[&str]| -> Result<()> {
        let out = Command::new("git")
            .arg("-C")
            .arg(&session)
            .args(["-c", "user.name=mockview", "-c", "user.email=mockview@localhost", "-c", "commit.gpgsign=false"])
            .args(args)
            .output()
            .context("running git")?;
        if !out.status.success() {
            bail!("git {} failed: {}", args.join(" "), String::from_utf8_lossy(&out.stderr));
        }
        Ok(())
    };
    ok(&["init", "-q"])?;
    ok(&["add", "-A"])?;
    ok(&["commit", "-q", "-m", "Starting point"])?;
    if let Some(env) = py.parent().and_then(Path::parent) {
        #[cfg(unix)]
        let _ = std::os::unix::fs::symlink(env, session.join(".venv"));
        #[cfg(windows)]
        let _ = std::os::windows::fs::symlink_dir(env, session.join(".venv"));
    }
    Ok(session)
}

/// Runs pytest in `dir` (only `files` if given). Returns the parsed result and the raw output.
pub fn pytest(py: &Path, dir: &Path, files: &[&str]) -> (TestRun, String) {
    let out = Command::new(py)
        .args(["-m", "pytest", "-q", "-rA", "-p", "no:cacheprovider", "--color=no", "--tb=short"])
        .args(files)
        .current_dir(dir)
        .env("PYTHONDONTWRITEBYTECODE", "1")
        .output();
    let Ok(out) = out else { return (TestRun::default(), String::new()) };
    let text = format!("{}{}", String::from_utf8_lossy(&out.stdout), String::from_utf8_lossy(&out.stderr));
    (parse_pytest(&text), text)
}

/// Per-test outcomes from pytest's `-rA` summary: (test name, passed).
pub fn pytest_outcomes(text: &str) -> Vec<(String, bool)> {
    text.lines()
        .filter_map(|l| {
            let (status, rest) = l.split_once(' ')?;
            let passed = match status {
                "PASSED" => true,
                "FAILED" | "ERROR" => false,
                _ => return None,
            };
            let id = rest.split(" - ").next().unwrap_or(rest).trim();
            Some((id.rsplit("::").next().unwrap_or(id).to_string(), passed))
        })
        .collect()
}

pub fn parse_pytest(text: &str) -> TestRun {
    let mut run = TestRun::default();
    let count = regex::Regex::new(r"(\d+) (passed|failed|errors?)\b").unwrap();
    if let Some(line) = text.lines().rev().find(|l| l.contains(" in ") && count.is_match(l)) {
        for c in count.captures_iter(line) {
            let n: u32 = c[1].parse().unwrap_or(0);
            match &c[2] {
                "passed" => run.ran += n,
                "failed" => {
                    run.ran += n;
                    run.failed = n;
                }
                _ => run.errors = n,
            }
        }
    }
    run.failing = pytest_outcomes(text).into_iter().filter(|(_, ok)| !ok).map(|(n, _)| n).collect();
    run
}

/// Runs `test_file` against a scratch copy of `code_dir` and returns pytest's output.
pub fn run_hidden(py: &Path, code_dir: &Path, test_file: &Path) -> Result<String> {
    let scratch = std::env::temp_dir().join(format!("mockview-check-{}", uuid::Uuid::new_v4()));
    std::fs::create_dir_all(&scratch)?;
    for p in walk(code_dir)? {
        let rel = p.strip_prefix(code_dir)?;
        if rel.file_name().is_some_and(|n| n.to_string_lossy().starts_with("test_")) {
            continue;
        }
        let dest = scratch.join(rel);
        std::fs::create_dir_all(dest.parent().unwrap())?;
        std::fs::copy(&p, dest)?;
    }
    std::fs::copy(test_file, scratch.join("test_mockview_hidden.py"))?;
    let (_, text) = pytest(py, &scratch, &["test_mockview_hidden.py"]);
    let _ = std::fs::remove_dir_all(&scratch);
    Ok(text)
}

fn grade_pack(ex: &Exercise, session: &Path) -> Result<String> {
    let py = crate::pyenv::python()?;
    let code = session.join("python");
    let (mine, _) = pytest(&py, &code, &[]);
    let mut s = format!("Your own tests (pytest in python/): {}\n\nHidden checks (one or more per planted bug):\n", mine.summary());
    let hidden = ex.hidden_tests();
    if !hidden.exists() {
        s.push_str("  (no answer key for this pack yet: run `mockview keys`)\n");
        return Ok(s);
    }
    let outcomes = pytest_outcomes(&run_hidden(&py, &code, &hidden)?);
    for (name, passed) in &outcomes {
        s.push_str(&format!("  {} {name}\n", if *passed { "PASS" } else { "FAIL" }));
    }
    let passed = outcomes.iter().filter(|(_, p)| *p).count();
    s.push_str(&format!("\n{passed}/{} hidden checks pass.\n", outcomes.len()));
    Ok(s)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_unittest_output() {
        let text = "test_a (t.T.test_a) ... ok\ntest_b (t.T.test_b) ... FAIL\n\nRan 2 tests in 0.001s\n\nFAILED (failures=1)\n";
        let run = parse_unittest(text);
        assert_eq!(run, TestRun { ran: 2, failed: 1, errors: 0, failing: vec!["test_b".into()] });
    }

    #[test]
    fn parses_pytest_output() {
        let text = "..F\n=== short test summary info ===\nPASSED test_x.py::test_a\nPASSED test_x.py::test_b\nFAILED test_x.py::test_c - assert 1 == 2\n1 failed, 2 passed in 0.03s\n";
        let run = parse_pytest(text);
        assert_eq!(run, TestRun { ran: 3, failed: 1, errors: 0, failing: vec!["test_c".into()] });
    }

    #[test]
    fn hides_pm_notes_from_the_brief() {
        let brief = "Treat the interviewer as the PM: ask questions (there is\na list to start from in `PROJECT_MANAGER_NOTES.md`).\n\n1. `CANDIDATE_BRIEF.md`: x\n2. `PROJECT_MANAGER_NOTES.md`: y\n3. `SETUP.md`: z\n4. `SELF_REVIEW_AFTER.md`: w\n";
        assert_eq!(without_hidden_docs(brief), "Treat the interviewer as the PM: ask questions.\n\n1. `CANDIDATE_BRIEF.md`: x\n2. `SETUP.md`: z\n");
    }
}
