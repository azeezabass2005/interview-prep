use std::path::{Path, PathBuf};
use std::process::Stdio;
use std::time::Duration;

use anyhow::{anyhow, bail, Context, Result};
use base64::Engine;
use serde_json::{json, Value};
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader, Lines};
use tokio::process::{Child, ChildStdin, ChildStdout, Command};

#[derive(Debug, Clone)]
pub struct SessionSpec {
    pub system_prompt_file: PathBuf,
    pub cwd: PathBuf,
    pub add_dirs: Vec<PathBuf>,
    pub tools: Vec<String>,
    pub model: String,
}

pub struct Session {
    spec: SessionSpec,
    id: String,
    started: bool,
    child: Option<Child>,
    stdin: Option<ChildStdin>,
    stdout: Option<Lines<BufReader<ChildStdout>>>,
}

#[derive(Debug, Clone, Default)]
pub struct TurnResult {
    pub text: String,
    pub cost_usd: f64,
}

pub enum Block {
    Text(String),
    Jpeg(Vec<u8>),
}

impl Session {
    pub fn new(spec: SessionSpec) -> Self {
        Self { spec, id: uuid::Uuid::new_v4().to_string(), started: false, child: None, stdin: None, stdout: None }
    }

    fn spawn(&mut self) -> Result<()> {
        let mut cmd = Command::new("claude");
        cmd.args(["-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose"])
            .arg("--include-partial-messages")
            .arg(if self.started { "--resume" } else { "--session-id" })
            .arg(&self.id)
            .arg("--system-prompt-file")
            .arg(&self.spec.system_prompt_file)
            .arg("--strict-mcp-config")
            .args(["--settings", r#"{"hooks":{},"disableAllHooks":true}"#]);
        let tools = self.spec.tools.join(",");
        cmd.args(["--tools", &tools]);
        if !tools.is_empty() {
            cmd.args(["--allowed-tools", &tools]);
        }
        for d in &self.spec.add_dirs {
            cmd.arg("--add-dir").arg(d);
        }
        if !self.spec.model.is_empty() {
            cmd.args(["--model", &self.spec.model]);
        }
        let stderr = std::fs::OpenOptions::new().create(true).append(true).open(self.spec.cwd.join("claude-stderr.log"));
        let mut child = cmd
            .current_dir(&self.spec.cwd)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(stderr.map(Stdio::from).unwrap_or_else(|_| Stdio::null()))
            .kill_on_drop(true)
            .spawn()
            .context("starting claude (is Claude Code installed and logged in?)")?;
        self.stdin = child.stdin.take();
        self.stdout = Some(BufReader::new(child.stdout.take().unwrap()).lines());
        self.child = Some(child);
        self.started = true;
        Ok(())
    }

    fn alive(&mut self) -> bool {
        match self.child.as_mut() {
            Some(c) => matches!(c.try_wait(), Ok(None)),
            None => false,
        }
    }

    pub async fn turn<F: FnMut(&str)>(&mut self, blocks: Vec<Block>, mut on_delta: F) -> Result<TurnResult> {
        for attempt in 0..2 {
            if !self.alive() {
                self.spawn()?;
            }
            match self.try_turn(&blocks, &mut on_delta).await {
                Ok(r) => return Ok(r),
                Err(e) if attempt == 0 => {
                    tracing::warn!("claude turn failed, restarting session: {e:#}");
                    if let Some(mut c) = self.child.take() {
                        let _ = c.kill().await;
                    }
                }
                Err(e) => return Err(e),
            }
        }
        unreachable!()
    }

    async fn try_turn<F: FnMut(&str)>(&mut self, blocks: &[Block], on_delta: &mut F) -> Result<TurnResult> {
        let content: Vec<Value> = blocks
            .iter()
            .map(|b| match b {
                Block::Text(t) => json!({"type": "text", "text": t}),
                Block::Jpeg(bytes) => json!({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                    "data": base64::engine::general_purpose::STANDARD.encode(bytes)}}),
            })
            .collect();
        let msg = json!({"type": "user", "message": {"role": "user", "content": content}});
        let stdin = self.stdin.as_mut().ok_or_else(|| anyhow!("claude stdin closed"))?;
        stdin.write_all(format!("{msg}\n").as_bytes()).await?;
        stdin.flush().await?;
        let lines = self.stdout.as_mut().ok_or_else(|| anyhow!("claude stdout closed"))?;
        let mut streamed = String::new();
        loop {
            let line = tokio::time::timeout(Duration::from_secs(180), lines.next_line())
                .await
                .map_err(|_| anyhow!("claude did not answer within 3 minutes"))??
                .ok_or_else(|| anyhow!("claude exited"))?;
            let Ok(ev) = serde_json::from_str::<Value>(&line) else { continue };
            match ev["type"].as_str() {
                Some("stream_event") => {
                    let e = &ev["event"];
                    if e["type"] == "content_block_delta" && e["delta"]["type"] == "text_delta" {
                        if let Some(t) = e["delta"]["text"].as_str() {
                            streamed.push_str(t);
                            on_delta(t);
                        }
                    }
                    if e["type"] == "message_start" && !streamed.is_empty() {
                        streamed.push('\n');
                        on_delta("\n");
                    }
                }
                Some("result") => {
                    if ev["is_error"].as_bool() == Some(true) {
                        bail!("claude error: {}", ev["result"]);
                    }
                    let text = ev["result"].as_str().map(str::to_string).unwrap_or(streamed);
                    return Ok(TurnResult { text, cost_usd: ev["total_cost_usd"].as_f64().unwrap_or(0.0) });
                }
                _ => {}
            }
        }
    }

    pub async fn close(&mut self) {
        self.stdin = None;
        if let Some(mut c) = self.child.take() {
            let _ = tokio::time::timeout(Duration::from_secs(5), c.wait()).await;
            let _ = c.kill().await;
        }
    }
}

pub async fn oneshot(prompt: &str, system: &str, cwd: &Path, add_dirs: &[PathBuf], tools: &[&str], model: &str) -> Result<String> {
    let mut cmd = Command::new("claude");
    cmd.args(["-p", "--output-format", "json", "--strict-mcp-config", "--system-prompt", system]);
    let tools = tools.join(",");
    cmd.args(["--tools", &tools]);
    if !tools.is_empty() {
        cmd.args(["--allowed-tools", &tools]);
    }
    for d in add_dirs {
        cmd.arg("--add-dir").arg(d);
    }
    if !model.is_empty() {
        cmd.args(["--model", model]);
    }
    let mut child = cmd
        .current_dir(cwd)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .kill_on_drop(true)
        .spawn()
        .context("starting claude")?;
    child.stdin.take().unwrap().write_all(prompt.as_bytes()).await?;
    let out = tokio::time::timeout(Duration::from_secs(900), child.wait_with_output())
        .await
        .map_err(|_| anyhow!("claude took longer than 15 minutes"))??;
    let v: Value = serde_json::from_slice(&out.stdout)
        .with_context(|| format!("unexpected claude output: {}", String::from_utf8_lossy(&out.stderr)))?;
    if v["is_error"].as_bool() == Some(true) {
        bail!("claude error: {}", v["result"]);
    }
    Ok(v["result"].as_str().unwrap_or_default().to_string())
}
