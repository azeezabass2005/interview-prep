use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::Arc;

use anyhow::{bail, Context, Result};

use crate::config::Config;
use crate::kit::{self, Exercise};

const CHECK_PY: &str = r#"import os, re, shutil, subprocess, sys, tempfile

def run(code_dir):
    d = tempfile.mkdtemp()
    for root, dirs, files in os.walk(code_dir):
        dirs[:] = [x for x in dirs if x != "__pycache__"]
        for f in files:
            if f.startswith("test_"):
                continue
            src = os.path.join(root, f)
            dst = os.path.join(d, os.path.relpath(src, code_dir))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
    shutil.copy("test_hidden.py", os.path.join(d, "test_mockview_hidden.py"))
    out = subprocess.run([sys.executable, "-m", "pytest", "-q", "-rA", "-p", "no:cacheprovider", "--color=no", "--tb=line",
                          "test_mockview_hidden.py"], cwd=d, capture_output=True, text=True,
                         env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    shutil.rmtree(d)
    return out.stdout + out.stderr

def outcomes(text):
    res = {}
    for line in text.splitlines():
        status, _, rest = line.partition(" ")
        if status in ("PASSED", "FAILED", "ERROR"):
            res[rest.split(" - ")[0].split("::")[-1]] = (status == "PASSED", rest)
    return res

shipped_text, fixed_text = run("pack/python"), run("fixed")
shipped, fixed = outcomes(shipped_text), outcomes(fixed_text)
if not shipped:
    print(shipped_text)
problems = []
for name in sorted(set(shipped) | set(fixed)):
    s, f = shipped.get(name, (None, "")), fixed.get(name, (None, ""))
    print(f"{name}: shipped={'pass' if s[0] else 'FAIL'} fixed={'pass' if f[0] else 'FAIL'}")
    if not s[0] and s[1]:
        print(f"    on shipped: {s[1]}")
    if not re.match(r"test_b\d+_", name):
        problems.append(f"{name} isn't named test_b<N>_...")
    if s[0]:
        problems.append(f"{name} passes on the shipped code")
    if not f[0]:
        problems.append(f"{name} fails on fixed/: {f[1]}")
if not shipped:
    problems.append("no tests ran")
print("\nALL GOOD" if not problems else "\nPROBLEMS:\n- " + "\n- ".join(problems))
"#;

fn hash(files: &[(PathBuf, Vec<u8>)]) -> String {
    let mut h: u64 = 0xcbf29ce484222325;
    for (path, bytes) in files {
        for b in path.to_string_lossy().bytes().chain(bytes.iter().copied()) {
            h ^= b as u64;
            h = h.wrapping_mul(0x100000001b3);
        }
    }
    format!("{h:016x}")
}

fn source(cfg: &Config, ex: &Exercise) -> Result<Vec<(PathBuf, Vec<u8>)>> {
    let files = kit::pristine_files(&cfg.kit(), &ex.dir)?;
    Ok(files.into_iter().filter(|(p, _)| !p.starts_with("cpp") && !p.starts_with("java")).collect())
}

/// Whether the pack has an answer key that matches its current code.
pub fn ready(cfg: &Config, ex: &Exercise) -> bool {
    if !ex.pack {
        return true;
    }
    let stored = std::fs::read_to_string(ex.notes_dir.join("source.hash")).unwrap_or_default();
    ["NOTES.md", "test_hidden.py", "fixes.diff"].iter().all(|f| ex.notes_dir.join(f).exists())
        && source(cfg, ex).is_ok_and(|s| hash(&s) == stored.trim())
}

/// Generates the answer key if it's missing or stale.
pub async fn ensure(cfg: &Config, ex: &Exercise, progress: impl Fn(&str)) -> Result<()> {
    if ready(cfg, ex) {
        return Ok(());
    }
    progress(&format!("Preparing the interviewer's answer key for {} (one time, about 3–8 minutes)…", ex.id()));
    generate(cfg, ex, progress).await
}

fn verify(py: &Path, work: &Path) -> Vec<String> {
    let mut problems = Vec::new();
    let notes = std::fs::read_to_string(work.join("NOTES.md")).unwrap_or_default();
    let bugs: std::collections::BTreeSet<String> = regex::Regex::new(r"(?m)^### B(\d+)\b").unwrap().captures_iter(&notes).map(|c| c[1].to_string()).collect();
    if bugs.is_empty() {
        problems.push("NOTES.md is missing or has no '### B1 · …' bug sections".into());
    }
    if !notes.contains("## PM answers") {
        problems.push("NOTES.md has no '## PM answers' table".into());
    }
    let tests = work.join("test_hidden.py");
    if !tests.exists() {
        problems.push("test_hidden.py is missing".into());
        return problems;
    }
    let outcome = |dir: &Path| kit::run_hidden(py, dir, &tests).map(|t| kit::pytest_outcomes(&t)).unwrap_or_default();
    let shipped = outcome(&work.join("pack/python"));
    let fixed = outcome(&work.join("fixed"));
    if shipped.is_empty() {
        problems.push("test_hidden.py runs no tests (import error?)".into());
    }
    let id = regex::Regex::new(r"^test_b(\d+)_").unwrap();
    let mut tested = std::collections::BTreeSet::new();
    for (name, passed) in &shipped {
        match id.captures(name) {
            Some(c) => {
                tested.insert(c[1].to_string());
            }
            None => problems.push(format!("{name} isn't named test_b<N>_…")),
        }
        if *passed {
            problems.push(format!("{name} passes on the shipped code"));
        }
    }
    for (name, passed) in &fixed {
        if !passed {
            problems.push(format!("{name} fails on fixed/"));
        }
    }
    for b in bugs.difference(&tested) {
        problems.push(format!("B{b} in NOTES.md has no test_b{b}_ test"));
    }
    problems
}

pub async fn generate(cfg: &Config, ex: &Exercise, progress: impl Fn(&str)) -> Result<()> {
    let py = crate::pyenv::python()?;
    let files = source(cfg, ex)?;
    let work = ex.notes_dir.join("work");
    let _ = std::fs::remove_dir_all(&work);
    for (rel, bytes) in &files {
        let path = work.join("pack").join(rel);
        std::fs::create_dir_all(path.parent().unwrap())?;
        std::fs::write(&path, bytes)?;
        if let Ok(inner) = rel.strip_prefix("python") {
            let fixed = work.join("fixed").join(inner);
            std::fs::create_dir_all(fixed.parent().unwrap())?;
            std::fs::write(fixed, bytes)?;
        }
    }
    std::fs::write(work.join("check.py"), CHECK_PY)?;
    let template = std::fs::read_to_string(cfg.prompts_dir().join("keygen.md")).context("missing prompts/keygen.md")?;
    let system = template.replace("{{python}}", &py.to_string_lossy());
    let mut prompt = format!("Write the answer key for the practice pack in the current directory (round {}, codename {}).", ex.round, ex.name);
    let mut problems = Vec::new();
    for attempt in 1..=3 {
        progress(&format!("  {}: attempt {attempt}: writing notes, fixes and hidden tests…", ex.id()));
        crate::claude::oneshot(&prompt, &system, &work, &[], &["Read", "Write", "Edit", "Glob", "Grep", "Bash"], &cfg.claude.model).await?;
        problems = verify(&py, &work);
        if problems.is_empty() {
            break;
        }
        progress(&format!("  {}: verification found {} problem(s); retrying", ex.id(), problems.len()));
        prompt = format!(
            "You already started the answer key for this pack (round {}, codename {}); the files you wrote are in the current directory. \
             An independent check found these problems. Fix them, then run check.py until it reports ALL GOOD:\n- {}",
            ex.round,
            ex.name,
            problems.join("\n- ")
        );
    }
    if !problems.is_empty() {
        bail!("couldn't produce a verified answer key for {} (files kept in {}):\n- {}", ex.id(), work.display(), problems.join("\n- "));
    }
    for f in ["NOTES.md", "test_hidden.py"] {
        std::fs::copy(work.join(f), ex.notes_dir.join(f))?;
    }
    let diff = Command::new("git").args(["diff", "--no-index", "--no-color", "--src-prefix=a/", "--dst-prefix=b/", "pack/python", "fixed"]).current_dir(&work).output()?;
    let diff = String::from_utf8_lossy(&diff.stdout).replace("a/pack/python/", "a/python/").replace("b/fixed/", "b/python/");
    std::fs::write(ex.notes_dir.join("fixes.diff"), diff)?;
    std::fs::write(ex.notes_dir.join("source.hash"), hash(&files))?;
    std::fs::remove_dir_all(&work)?;
    progress(&format!("  {}: answer key ready", ex.id()));
    Ok(())
}

/// Generates missing answer keys for several packs, a few at a time.
pub async fn generate_many(cfg: &Config, exercises: Vec<Exercise>, force: bool) -> Result<()> {
    let todo: Vec<Exercise> = exercises.into_iter().filter(|e| e.pack && (force || !ready(cfg, e))).collect();
    if todo.is_empty() {
        println!("Every pack already has an answer key.");
        return Ok(());
    }
    crate::pyenv::python()?;
    println!("Writing {} answer key(s), three at a time…", todo.len());
    let limit = Arc::new(tokio::sync::Semaphore::new(3));
    let mut set = tokio::task::JoinSet::new();
    for ex in todo {
        let (cfg, limit) = (cfg.clone(), limit.clone());
        set.spawn(async move {
            let _permit = limit.acquire().await;
            let r = generate(&cfg, &ex, |m| println!("{m}")).await;
            (ex, r)
        });
    }
    let mut failed = Vec::new();
    while let Some(done) = set.join_next().await {
        let (ex, r) = done?;
        if let Err(e) = r {
            println!("✗ {}: {e:#}", ex.id());
            failed.push(ex.id());
        }
    }
    if !failed.is_empty() {
        bail!("{} answer key(s) failed: {}", failed.len(), failed.join(", "));
    }
    println!("All answer keys ready.");
    Ok(())
}
