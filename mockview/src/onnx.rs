use std::path::Path;
use std::sync::OnceLock;

use anyhow::{anyhow, Result};
use ort::environment::Environment;
use ort::session::Session;

static ENV: OnceLock<Environment> = OnceLock::new();

pub fn session(path: &Path, threads: usize) -> Result<Session> {
    if ENV.get().is_none() {
        let env = ort::init().with_name("mockview").build().map_err(|e| anyhow!("onnx runtime: {e}"))?;
        let _ = ENV.set(env);
    }
    let env = ENV.get().unwrap();
    Session::builder(env)
        .map_err(|e| anyhow!("{e}"))?
        .with_intra_threads(threads)
        .map_err(|e| anyhow!("{e}"))?
        .commit_from_file(path)
        .map_err(|e| anyhow!("loading {}: {e}", path.display()))
}
