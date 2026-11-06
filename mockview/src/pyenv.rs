use std::path::PathBuf;
use std::process::Command;
use std::sync::OnceLock;

use anyhow::{anyhow, bail, Context, Result};

/// mockview's own Python environment with pytest, shared by every practice session (linked into each one as `.venv`).
pub fn env_dir() -> PathBuf {
    dirs::data_dir().unwrap_or_else(|| PathBuf::from(".")).join("mockview/python")
}

fn exe() -> PathBuf {
    if cfg!(windows) {
        env_dir().join("Scripts").join("python.exe")
    } else {
        env_dir().join("bin").join("python")
    }
}

fn has_pytest(py: &PathBuf) -> bool {
    Command::new(py).args(["-c", "import pytest"]).output().is_ok_and(|o| o.status.success())
}

fn system_python() -> Option<&'static str> {
    ["python3", "python", "py"].into_iter().find(|p| Command::new(p).arg("--version").output().is_ok_and(|o| o.status.success()))
}

fn create() -> Result<PathBuf> {
    let py = exe();
    if has_pytest(&py) {
        return Ok(py);
    }
    let base = system_python().ok_or_else(|| anyhow!("Python 3 isn't installed (tried python3, python and py)"))?;
    eprintln!("Setting up mockview's Python environment with pytest (one time)…");
    let out = Command::new(base).args(["-m", "venv"]).arg(env_dir()).output().context("creating the Python environment")?;
    if !out.status.success() {
        bail!("python -m venv failed: {}", String::from_utf8_lossy(&out.stderr));
    }
    let out = Command::new(&py).args(["-m", "pip", "install", "-q", "--disable-pip-version-check", "pytest"]).output().context("installing pytest")?;
    if !out.status.success() {
        bail!("installing pytest failed: {}", String::from_utf8_lossy(&out.stderr));
    }
    Ok(py)
}

/// The Python interpreter to run practice-pack tests with, creating the environment on first use.
pub fn python() -> Result<PathBuf> {
    static PY: OnceLock<Result<PathBuf, String>> = OnceLock::new();
    PY.get_or_init(|| create().map_err(|e| format!("{e:#}"))).clone().map_err(|e| anyhow!(e))
}
