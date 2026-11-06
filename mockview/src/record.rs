use std::fs::{self, File, OpenOptions};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::time::Instant;

use anyhow::Result;
use serde::{Deserialize, Serialize};
use serde_json::json;

pub struct Recorder {
    pub dir: PathBuf,
    started: Instant,
    transcript: File,
    notes: File,
    timeline: File,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Line {
    pub t: f64,
    pub speaker: String,
    pub phase: String,
    pub text: String,
}

impl Recorder {
    pub fn create(runs: &Path, id: &str) -> Result<Self> {
        let dir = runs.join(id);
        fs::create_dir_all(dir.join("screenshots"))?;
        let open = |name: &str| OpenOptions::new().create(true).append(true).open(dir.join(name));
        Ok(Self {
            transcript: open("transcript.jsonl")?,
            notes: open("notes.jsonl")?,
            timeline: open("timeline.jsonl")?,
            dir,
            started: Instant::now(),
        })
    }

    pub fn elapsed(&self) -> f64 {
        self.started.elapsed().as_secs_f64()
    }

    pub fn say(&mut self, speaker: &str, phase: &str, text: &str) -> Result<()> {
        let line = Line { t: self.elapsed(), speaker: speaker.into(), phase: phase.into(), text: text.into() };
        writeln!(self.transcript, "{}", serde_json::to_string(&line)?)?;
        Ok(())
    }

    pub fn note(&mut self, phase: &str, text: &str) -> Result<()> {
        writeln!(self.notes, "{}", json!({"t": self.elapsed(), "phase": phase, "notes": text}))?;
        Ok(())
    }

    pub fn event(&mut self, kind: &str, detail: serde_json::Value) -> Result<()> {
        writeln!(self.timeline, "{}", json!({"t": self.elapsed(), "event": kind, "detail": detail}))?;
        Ok(())
    }

    pub fn write(&self, name: &str, content: &str) -> Result<()> {
        fs::write(self.dir.join(name), content)?;
        Ok(())
    }

    pub fn screenshot_path(&self) -> PathBuf {
        self.dir.join("screenshots").join(format!("{:05}.jpg", self.elapsed() as u64))
    }
}

pub fn read_transcript(run: &Path) -> Vec<Line> {
    fs::read_to_string(run.join("transcript.jsonl"))
        .unwrap_or_default()
        .lines()
        .filter_map(|l| serde_json::from_str(l).ok())
        .collect()
}

pub fn mmss(t: f64) -> String {
    let s = t.max(0.0) as u64;
    format!("{:02}:{:02}", s / 60, s % 60)
}
