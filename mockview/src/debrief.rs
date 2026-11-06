use std::path::{Path, PathBuf};

use anyhow::{Context, Result};
use regex::Regex;
use serde_json::{json, Value};

use crate::config::Config;

pub const CRITERIA: &[(&str, &str)] = &[
    ("understand_code", "Understand code"),
    ("use_ai", "Use AI critically"),
    ("testing", "Testing & verification"),
    ("problem_solving", "Problem solving"),
    ("communication", "Communication"),
    ("collaboration", "Collaboration"),
    ("clarifying_questions", "Clarifying questions"),
    ("introduction", "Introduction"),
    ("resume_depth", "Resume depth"),
    ("past_problem", "Past problem"),
    ("deep_dive", "Data structures"),
    ("feature_design", "Feature design"),
    ("candidate_questions", "Your questions"),
];

const SECTIONS: &[&str] = &["overview", "exercise", "timeline", "conversation", "ai_communication", "action_plan"];

fn run_dirs(runs: &Path) -> Vec<PathBuf> {
    let mut dirs: Vec<PathBuf> = std::fs::read_dir(runs)
        .map(|e| e.flatten().map(|e| e.path()).filter(|p| p.is_dir()).collect())
        .unwrap_or_default();
    dirs.sort();
    dirs
}

/// Scores of the most recent `n` runs that have a debrief (oldest first).
pub fn previous_scores(runs: &Path, n: usize) -> Vec<Value> {
    let all: Vec<Value> = run_dirs(runs)
        .iter()
        .filter_map(|d| std::fs::read_to_string(d.join("scores.json")).ok())
        .filter_map(|t| serde_json::from_str(&t).ok())
        .collect();
    all[all.len().saturating_sub(n)..].to_vec()
}

pub struct Debrief {
    pub report: PathBuf,
    pub spoken_summary: Option<String>,
    pub scores: Option<Value>,
}

fn prepare_files(cfg: &Config, run: &Path) -> Result<(Value, Vec<PathBuf>)> {
    let meta: Value = serde_json::from_str(&std::fs::read_to_string(run.join("meta.json")).context("run has no meta.json")?)?;
    let kit = meta["kit"].as_str().map(PathBuf::from).unwrap_or_else(|| cfg.kit());
    let name = meta["exercise"]["name"].as_str().unwrap_or_default();
    let exercise = crate::kit::Exercise::new(&kit, meta["exercise"]["round"].as_u64().unwrap_or(1) as u8, name);
    let copy = |from: PathBuf, to: &str| {
        let _ = std::fs::copy(from, run.join(to));
    };
    let scorecard = kit.join("SCORECARD.md");
    copy(if scorecard.exists() { scorecard } else { cfg.prompts_dir().join("scorecard.md") }, "scorecard.md");
    copy(exercise.notes_dir.join("NOTES.md"), "interviewer-notes.md");
    let (fixes, fixes_name) = exercise.reference_fixes();
    copy(fixes, fixes_name);
    copy(exercise.hidden_tests(), "reference-hidden-tests.py");
    if exercise.pack {
        for (path, bytes) in crate::kit::pristine_files(&kit, &exercise.dir).unwrap_or_default() {
            let to = match path.to_string_lossy().as_ref() {
                "PROJECT_MANAGER_NOTES.md" => "reference-pm-questions.md",
                "SELF_REVIEW_AFTER.md" => "reference-self-review.md",
                _ => continue,
            };
            std::fs::write(run.join(to), bytes)?;
        }
    }
    std::fs::write(run.join("exercise-spec.md"), exercise.spec())?;
    std::fs::write(run.join("resume.txt"), crate::interview::resume_text(cfg).unwrap_or_else(|| "No resume provided.".into()))?;
    let previous: Vec<Value> = run_dirs(&cfg.runs_dir())
        .into_iter()
        .filter(|d| d != run)
        .filter_map(|d| {
            let s: Value = serde_json::from_str(&std::fs::read_to_string(d.join("scores.json")).ok()?).ok()?;
            Some(json!({"run": d.file_name()?.to_string_lossy(), "verdict": s["verdict"], "overall": s["overall"], "scores": s["scores"],
                        "weaknesses": s["weaknesses"], "action_items": s["action_items"]}))
        })
        .collect();
    std::fs::write(run.join("previous.json"), serde_json::to_string_pretty(&previous)?)?;
    let mut readable = String::new();
    for l in crate::record::read_transcript(run) {
        readable.push_str(&format!("[{}] ({}) {}: {}\n", crate::record::mmss(l.t), l.phase, l.speaker, l.text));
    }
    std::fs::write(run.join("transcript.txt"), readable)?;
    let mut dirs = vec![run.to_path_buf()];
    if let Some(session) = meta["session_dir"].as_str() {
        if Path::new(session).exists() {
            dirs.push(PathBuf::from(session));
        }
    }
    Ok((meta, dirs))
}

fn prompt(cfg: &Config, part: &str) -> Result<String> {
    let dir = cfg.prompts_dir().join("debrief");
    let common = std::fs::read_to_string(dir.join("common.md")).context("missing prompts/debrief/common.md")?;
    let part = std::fs::read_to_string(dir.join(format!("{part}.md"))).with_context(|| format!("missing prompts/debrief/{part}.md"))?;
    Ok(format!("{common}\n\n# Your task\n\n{part}"))
}

async fn score(cfg: &Config, run: &Path, dirs: &[PathBuf]) -> Result<Value> {
    let system = prompt(cfg, "scores")?;
    let re = Regex::new(r"(?s)<scores>\s*(.*?)\s*</scores>").unwrap();
    let mut last = String::new();
    for _ in 0..2 {
        let reply = crate::claude::oneshot("Score the mock interview in the current directory.", &system, run, dirs, &["Read", "Glob", "Grep"], &cfg.claude.model).await?;
        let raw = re.captures(&reply).map(|c| c[1].to_string()).unwrap_or_else(|| reply.clone());
        let raw = raw.trim().trim_start_matches("```json").trim_start_matches("```").trim_end_matches("```");
        if let Ok(v) = serde_json::from_str::<Value>(raw) {
            return Ok(v);
        }
        last = reply;
    }
    std::fs::write(run.join("evaluator-raw.txt"), &last)?;
    anyhow::bail!("the evaluator didn't return valid scores (see evaluator-raw.txt)")
}

pub async fn write(cfg: &Config, run: &Path, progress: impl Fn(&str)) -> Result<Debrief> {
    let (meta, dirs) = prepare_files(cfg, run)?;
    progress("scoring the interview…");
    let scores = score(cfg, run, &dirs).await?;
    std::fs::write(run.join("scores.json"), serde_json::to_string_pretty(&scores)?)?;

    progress("writing the six report sections in parallel…");
    let mut set = tokio::task::JoinSet::new();
    for (i, section) in SECTIONS.iter().enumerate() {
        let system = prompt(cfg, section)?;
        let (run, dirs, model) = (run.to_path_buf(), dirs.clone(), cfg.claude.model.clone());
        set.spawn(async move {
            let text = crate::claude::oneshot("Write your section of the debrief for the mock interview in the current directory.", &system, &run, &dirs, &["Read", "Glob", "Grep"], &model).await;
            (i, text)
        });
    }
    let mut parts: Vec<(usize, String)> = Vec::new();
    while let Some(done) = set.join_next().await {
        let (i, text) = done?;
        let text = text.unwrap_or_else(|e| format!("## {}\n\n_This section couldn't be written: {e:#}. Run `mockview debrief {}` to retry._", SECTIONS[i], run.display()));
        progress(&format!("section {}/{} done", parts.len() + 1, SECTIONS.len()));
        parts.push((i, text));
    }
    parts.sort_by_key(|(i, _)| *i);

    let title = meta["exercise"]["title"].as_str().unwrap_or("Mock interview");
    let started = meta["started"].as_str().unwrap_or("").get(..16).unwrap_or("").replace('T', " ");
    let minutes = meta["elapsed_seconds"].as_f64().unwrap_or(0.0) / 60.0;
    let overall = &scores["overall"];
    let mut report = format!(
        "# Debrief: {title}\n\n{started} · interviewer {} ({}) · {minutes:.0} minutes\n\n\
         **Verdict: {}** · **Overall {}/{} ({}%)** · bugs fixed {}/{}\n\n> {}\n\n\
         Contents: 1. Verdict and scorecard · 2. The exercise, solved · 3. Minute by minute · 4. Talking about yourself and your thinking · \
         5. AI assistant and communication · 6. Improvement plan\n\n---\n\n",
        meta["persona"]["name"].as_str().unwrap_or(""),
        meta["persona"]["team"].as_str().unwrap_or(""),
        scores["verdict"].as_str().unwrap_or("?"),
        overall["score_sum"],
        overall["max"],
        overall["percent"],
        scores["bugs"]["fixed"],
        scores["bugs"]["total"],
        scores["verdict_reason"].as_str().unwrap_or("")
    );
    for (_, text) in parts {
        report.push_str(text.trim());
        report.push_str("\n\n---\n\n");
    }
    report.push_str("_Files: transcript.txt (everything said), diff.patch (your changes), grade.txt (hidden checks), screenshots/._\n");
    let report_path = run.join("debrief.md");
    std::fs::write(&report_path, &report)?;
    Ok(Debrief { report: report_path, spoken_summary: scores["spoken_summary"].as_str().map(str::to_string), scores: Some(scores) })
}

pub fn print_summary(scores: &Value) {
    let overall = &scores["overall"];
    println!(
        "\n  Verdict: {}    Overall: {}/{} ({}%)    Bugs fixed: {}/{}\n",
        scores["verdict"].as_str().unwrap_or("?").to_uppercase(),
        overall["score_sum"],
        overall["max"],
        overall["percent"],
        scores["bugs"]["fixed"],
        scores["bugs"]["total"]
    );
    for (key, label) in CRITERIA {
        let s = &scores["scores"][key];
        let score = s["score"].as_f64();
        let shown = score.map(|v| format!("{v}/4")).unwrap_or_else(|| "n/a".into());
        let bar: String = match score.map(|v| v.round() as usize) {
            Some(n) => "■".repeat(n) + &"□".repeat(4 - n.min(4)),
            None => "    ".into(),
        };
        println!("  {label:<22} {bar}  {shown:<5} {}", s["evidence"].as_str().unwrap_or("").chars().take(90).collect::<String>());
    }
    println!("\n  Top things to change:");
    for a in scores["action_items"].as_array().into_iter().flatten() {
        println!("   • {}", a.as_str().unwrap_or_default());
    }
}

fn bar(score: Option<f64>) -> char {
    match score.map(|s| s.round() as i64) {
        Some(1) => '▂',
        Some(2) => '▄',
        Some(3) => '▆',
        Some(4) => '█',
        _ => '·',
    }
}

pub fn progress(cfg: &Config) -> Result<()> {
    let runs: Vec<(String, Value, Value)> = run_dirs(&cfg.runs_dir())
        .iter()
        .filter_map(|d| {
            let s: Value = serde_json::from_str(&std::fs::read_to_string(d.join("scores.json")).ok()?).ok()?;
            let m: Value = serde_json::from_str(&std::fs::read_to_string(d.join("meta.json")).ok()?).unwrap_or(Value::Null);
            Some((d.file_name()?.to_string_lossy().to_string(), s, m))
        })
        .collect();
    if runs.is_empty() {
        println!("No debriefed interviews yet. Run `mockview interview` first.");
        return Ok(());
    }
    println!("{} debriefed interviews\n", runs.len());
    println!("{:<22} {:<8} {}", "Criterion", "Latest", "Trend (oldest → newest)");
    for (key, label) in CRITERIA {
        let series: Vec<Option<f64>> = runs.iter().map(|(_, s, _)| s["scores"][key]["score"].as_f64()).collect();
        let latest = series.iter().rev().flatten().next().map(|v| format!("{v}/4")).unwrap_or_else(|| "-".into());
        let trend: String = series.iter().map(|v| bar(*v)).collect();
        println!("{label:<22} {latest:<8} {trend}");
    }
    println!("\nRecent interviews:");
    for (name, s, m) in runs.iter().rev().take(8) {
        let bugs = &s["bugs"];
        println!(
            "  {name}  {:<14} bugs fixed {}/{}  {}",
            s["verdict"].as_str().unwrap_or("?"),
            bugs["fixed"].as_i64().unwrap_or(0),
            bugs["total"].as_i64().unwrap_or(0),
            m["persona"]["name"].as_str().unwrap_or("")
        );
    }
    let mut counts: std::collections::BTreeMap<String, usize> = Default::default();
    for (_, s, _) in &runs {
        for w in s["weaknesses"].as_array().into_iter().flatten() {
            let key: String = w.as_str().unwrap_or_default().chars().take(90).collect();
            *counts.entry(key).or_default() += 1;
        }
    }
    let mut recurring: Vec<_> = counts.into_iter().filter(|(_, n)| *n > 1).collect();
    recurring.sort_by(|a, b| b.1.cmp(&a.1));
    if !recurring.is_empty() {
        println!("\nRecurring weaknesses:");
        for (w, n) in recurring.iter().take(5) {
            println!("  ({n}x) {w}");
        }
    }
    if let Some((_, last, _)) = runs.last() {
        println!("\nYour current action items:");
        for a in last["action_items"].as_array().into_iter().flatten() {
            println!("  - {}", a.as_str().unwrap_or_default());
        }
        if let Some(next) = last["next_exercise"].as_str() {
            println!("\nSuggested next exercise: {next}");
        }
    }
    Ok(())
}
