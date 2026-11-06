use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::time::{Duration, Instant, SystemTime};

use anyhow::{Context, Result};
use rand::seq::IndexedRandom;
use serde::Deserialize;
use serde_json::json;
use tokio::sync::mpsc::{UnboundedReceiver, UnboundedSender};

use crate::claude::{self, Block};
use crate::config::Config;
use crate::kit::{self, Exercise, TestRun};
use crate::record::{mmss, Recorder};
use crate::tts::split_reply;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Phase {
    Greeting,
    Intro,
    PastProblem,
    Setup,
    Coding,
    DeepDive,
    Questions,
    Close,
}

impl Phase {
    pub const ALL: [Phase; 8] =
        [Phase::Greeting, Phase::Intro, Phase::PastProblem, Phase::Setup, Phase::Coding, Phase::DeepDive, Phase::Questions, Phase::Close];

    pub fn key(self) -> &'static str {
        match self {
            Phase::Greeting => "greeting",
            Phase::Intro => "intro",
            Phase::PastProblem => "past_problem",
            Phase::Setup => "setup",
            Phase::Coding => "coding",
            Phase::DeepDive => "deep_dive",
            Phase::Questions => "questions",
            Phase::Close => "close",
        }
    }

    pub fn label(self) -> &'static str {
        match self {
            Phase::Greeting => "Greeting",
            Phase::Intro => "About you",
            Phase::PastProblem => "Past problem",
            Phase::Setup => "Exercise setup",
            Phase::Coding => "Coding",
            Phase::DeepDive => "Deep dive",
            Phase::Questions => "Your questions",
            Phase::Close => "Close",
        }
    }

    fn minutes(self) -> f64 {
        match self {
            Phase::Greeting => 2.0,
            Phase::Intro => 6.0,
            Phase::PastProblem => 4.0,
            Phase::Setup => 3.0,
            Phase::Coding => 30.0,
            Phase::DeepDive => 10.0,
            Phase::Questions => 3.0,
            Phase::Close => 2.0,
        }
    }

    fn instruction(self) -> &'static str {
        match self {
            Phase::Greeting => "Greet the candidate, introduce yourself and explain the format.",
            Phase::Intro => "Ask them to tell you about themselves, then follow up on their resume.",
            Phase::PastProblem => "Ask about a difficult technical problem they solved.",
            Phase::Setup => "The exercise is now open in their editor. Tell them, and ask them to read it and summarise it back to you.",
            Phase::Coding => "They should now be investigating and fixing. Let them drive; act as PM; check in as needed.",
            Phase::DeepDive => "Wrap up the coding. Ask about the data structures in their fixes, then give one feature request to discuss.",
            Phase::Questions => "Ask if they have any questions for you.",
            Phase::Close => "Thank them and close the interview, then send {\"end\": true}.",
        }
    }

    fn next(self) -> Option<Phase> {
        let i = Phase::ALL.iter().position(|p| *p == self)?;
        Phase::ALL.get(i + 1).copied()
    }

    fn watches_workspace(self) -> bool {
        matches!(self, Phase::Setup | Phase::Coding | Phase::DeepDive)
    }
}

#[derive(Debug, Clone, Deserialize)]
pub struct Persona {
    pub name: String,
    pub team: String,
    pub office: String,
    pub years: u32,
    pub voice: String,
    pub note: String,
}

#[derive(Deserialize)]
struct PersonaFile {
    persona: Vec<Persona>,
}

pub fn personas(cfg: &Config) -> Result<Vec<Persona>> {
    let text = std::fs::read_to_string(cfg.prompts_dir().join("personas.toml"))?;
    Ok(toml::from_str::<PersonaFile>(&text)?.persona)
}

pub enum Input {
    Said(String),
    NextPhase,
    Look,
    End,
}

pub enum Output {
    Delta(String),
    Interviewer(String),
    Candidate(String),
    Phase(Phase, f64),
    Status(String),
    Thinking(bool),
    Ended,
}

/// What the front end knows about live audio, so proactive turns never talk over anyone.
pub trait Activity: Send + Sync {
    fn busy(&self) -> bool;
}

pub struct NoActivity;
impl Activity for NoActivity {
    fn busy(&self) -> bool {
        false
    }
}

pub struct Prepared {
    pub cfg: Config,
    pub exercise: Exercise,
    pub persona: Persona,
    pub session_dir: PathBuf,
    pub recorder: Recorder,
    pub minutes: f64,
    claude: claude::Session,
}

impl Prepared {
    pub fn voice(&self) -> String {
        if self.cfg.tts.voice.is_empty() || self.cfg.tts.voice == "auto" {
            self.persona.voice.clone()
        } else {
            self.cfg.tts.voice.clone()
        }
    }
}

fn redact(text: &str) -> String {
    let email = regex::Regex::new(r"[\w.+-]+@[\w-]+\.[\w.]+").unwrap();
    let phone = regex::Regex::new(r"\+?\d[\d ()-]{8,}\d").unwrap();
    phone.replace_all(&email.replace_all(text, "[email]"), "[phone]").to_string()
}

pub fn resume_text(cfg: &Config) -> Option<String> {
    resume_raw(cfg).map(|t| redact(&t))
}

fn resume_raw(cfg: &Config) -> Option<String> {
    let dir = cfg.resume_dir();
    let md = ["resume.md", "resume.txt"].iter().map(|n| dir.join(n)).find(|p| p.exists());
    if let Some(p) = md {
        return std::fs::read_to_string(p).ok();
    }
    let pdf = std::fs::read_dir(&dir).ok()?.flatten().map(|e| e.path()).find(|p| p.extension().is_some_and(|e| e == "pdf"))?;
    let out = std::process::Command::new("pdftotext").args(["-layout"]).arg(&pdf).arg("-").output().ok()?;
    let text = String::from_utf8_lossy(&out.stdout).to_string();
    (!text.trim().is_empty()).then_some(text)
}

fn done_exercises(cfg: &Config) -> Vec<String> {
    let Ok(entries) = std::fs::read_dir(cfg.runs_dir()) else { return Vec::new() };
    entries
        .flatten()
        .filter_map(|e| std::fs::read_to_string(e.path().join("meta.json")).ok())
        .filter_map(|t| serde_json::from_str::<serde_json::Value>(&t).ok())
        .filter_map(|v| v["exercise"]["id"].as_str().map(str::to_string))
        .collect()
}

fn history(cfg: &Config) -> String {
    let scores = crate::debrief::previous_scores(&cfg.runs_dir(), 3);
    if scores.is_empty() {
        return String::new();
    }
    let mut s = String::from("## From this candidate's earlier mock interviews (probe these naturally, don't mention them)\n\n");
    for v in scores {
        for w in v["weaknesses"].as_array().into_iter().flatten().take(4) {
            s.push_str(&format!("- Weakness seen before: {}\n", w.as_str().unwrap_or_default()));
        }
        for a in v["action_items"].as_array().into_iter().flatten().take(3) {
            s.push_str(&format!("- They were working on: {}\n", a.as_str().unwrap_or_default()));
        }
    }
    s
}

pub fn choose_exercise(cfg: &Config, exercise: Option<&str>) -> Result<Exercise> {
    let kit_dir = cfg.kit();
    match exercise {
        Some(spec) => kit::resolve(&kit_dir, spec),
        None => kit::pick(&kit_dir, &cfg.interview.exercise_pool, &done_exercises(cfg)),
    }
}

pub fn prepare(cfg: &Config, exercise: Exercise, persona: Option<&str>, minutes: Option<f64>) -> Result<Prepared> {
    let kit_dir = cfg.kit();
    let all = personas(cfg)?;
    let persona = match persona {
        Some(name) => all
            .iter()
            .find(|p| p.name.to_lowercase().contains(&name.to_lowercase()))
            .cloned()
            .with_context(|| format!("no persona matching {name}"))?,
        None => all.choose(&mut rand::rng()).cloned().context("no personas defined")?,
    };
    let minutes = minutes.unwrap_or(cfg.interview.minutes as f64);
    let id = format!("{}-{}", chrono::Local::now().format("%Y-%m-%d-%H%M"), exercise.id());
    let recorder = Recorder::create(&cfg.runs_dir(), &id)?;
    let session_dir = kit::start_session(&kit_dir, &exercise)?;

    let resume = match resume_text(cfg) {
        Some(text) => format!("## Their resume\n\n{}", text.chars().take(15_000).collect::<String>()),
        None => "No resume was provided. Ask about their background and projects in general terms.".to_string(),
    };
    let template = std::fs::read_to_string(cfg.prompts_dir().join("interviewer.md"))?;
    let prompt = template
        .replace("{{name}}", &persona.name)
        .replace("{{team}}", &persona.team)
        .replace("{{office}}", &persona.office)
        .replace("{{years}}", &persona.years.to_string())
        .replace("{{note}}", &persona.note)
        .replace("{{resume}}", &resume)
        .replace("{{history}}", &history(cfg))
        .replace("{{exercise_title}}", &exercise.title())
        .replace("{{exercise_id}}", &exercise.id())
        .replace("{{exercise_format}}", exercise.format())
        .replace("{{spec}}", &exercise.spec())
        .replace("{{notes}}", &exercise.notes());
    let prompt_file = recorder.dir.join("interviewer-prompt.md");
    std::fs::write(&prompt_file, &prompt)?;
    recorder.write(
        "meta.json",
        &serde_json::to_string_pretty(&json!({
            "exercise": {"id": exercise.id(), "title": exercise.title(), "round": exercise.round, "name": exercise.name, "pack": exercise.pack},
            "kit": kit_dir,
            "persona": {"name": persona.name, "team": persona.team, "voice": persona.voice},
            "session_dir": session_dir,
            "minutes": minutes,
            "started": chrono::Local::now().to_rfc3339(),
            "model": cfg.claude.model,
            "stt_model": cfg.stt.model,
        }))?,
    )?;
    let claude = claude::Session::new(claude::SessionSpec {
        system_prompt_file: prompt_file,
        cwd: recorder.dir.clone(),
        add_dirs: vec![session_dir.clone()],
        tools: vec!["Read".into(), "Glob".into(), "Grep".into()],
        model: cfg.claude.model.clone(),
    });
    Ok(Prepared { cfg: cfg.clone(), exercise, persona, session_dir, recorder, minutes, claude })
}

struct Workspace {
    last_mtime: Option<SystemTime>,
    last_tests: TestRun,
    last_test_change: Instant,
    last_checked: Instant,
}

impl Workspace {
    fn refresh(&mut self, session: &Path) -> bool {
        self.last_checked = Instant::now();
        let mtime = kit::latest_mtime(session);
        if mtime == self.last_mtime {
            return false;
        }
        self.last_mtime = mtime;
        let run = kit::run_tests(session);
        let changed = run != self.last_tests;
        if kit::latest_test_mtime(session).is_some_and(|t| t.elapsed().map(|e| e < Duration::from_secs(30)).unwrap_or(false)) {
            self.last_test_change = Instant::now();
        }
        self.last_tests = run;
        changed
    }

    fn status(&self, session: &Path) -> String {
        let stat = kit::diff_stat(session).unwrap_or_default();
        let files = if stat.is_empty() { "no files changed yet".to_string() } else { stat.replace('\n', "; ") };
        format!("[workspace] {} | {}", self.last_tests.summary(), files)
    }
}

struct Core {
    p: Prepared,
    tx: UnboundedSender<Output>,
    activity: Arc<dyn Activity>,
    started: Instant,
    phase: Phase,
    phase_started: Instant,
    last_candidate: Instant,
    last_interviewer: Instant,
    last_proactive: Instant,
    last_check_in: Instant,
    nudged_tests: bool,
    hints: Vec<(Instant, u8)>,
    ws: Workspace,
    ended: bool,
    cost: f64,
}

impl Core {
    fn elapsed(&self) -> f64 {
        self.started.elapsed().as_secs_f64()
    }

    fn scale(&self) -> f64 {
        self.p.minutes / 60.0
    }

    fn phase_budget(&self, phase: Phase) -> f64 {
        phase.minutes() * 60.0 * self.scale()
    }

    fn phase_left(&self) -> f64 {
        self.phase_budget(self.phase) - self.phase_started.elapsed().as_secs_f64()
    }

    /// Hints are rationed: coding phase only, not in its first few minutes, spaced out, and never beyond level 2.
    fn hint_allowed(&self) -> Option<u8> {
        if self.phase != Phase::Coding {
            return None;
        }
        let budget = self.phase_budget(Phase::Coding);
        let into_coding = self.phase_started.elapsed().as_secs_f64();
        if into_coding < (5.0_f64 * 60.0).min(budget * 0.3) {
            return None;
        }
        if let Some((last, _)) = self.hints.last() {
            if last.elapsed().as_secs_f64() < (7.0_f64 * 60.0).min(budget * 0.25) {
                return None;
            }
        }
        Some(if self.hints.is_empty() { 1 } else { 2 })
    }

    fn header(&self) -> String {
        let hint = match self.hint_allowed() {
            Some(level) => format!("yes (level {level} at most, only if they are genuinely stuck)"),
            None => "no".to_string(),
        };
        format!(
            "[clock {} | phase: {} | {} left in this phase | hints given: {}, hint allowed: {}]",
            mmss(self.elapsed()),
            self.phase.key(),
            mmss(self.phase_left()),
            self.hints.len(),
            hint
        )
    }

    fn emit(&self, o: Output) {
        let _ = self.tx.send(o);
    }

    fn set_phase(&mut self, phase: Phase) -> Result<()> {
        self.phase = phase;
        self.phase_started = Instant::now();
        self.p.recorder.event("phase", json!({"phase": phase.key()}))?;
        self.emit(Output::Phase(phase, self.phase_budget(phase)));
        if phase == Phase::Setup {
            if let Err(e) = kit::open_in_editor(&self.p.cfg.editor.command, &self.p.session_dir) {
                self.emit(Output::Status(format!("couldn't open the editor: {e:#}")));
            }
            if self.p.cfg.editor.command != "none" {
                crate::layout::arrange(&self.p.cfg.layout.mode);
            }
            self.ws.refresh(&self.p.session_dir);
            self.last_check_in = Instant::now();
            self.ws.last_test_change = Instant::now();
        }
        Ok(())
    }

    async fn turn(&mut self, text: String, screenshot: bool) -> Result<()> {
        let mut blocks = vec![Block::Text(format!("{}\n{}", self.header(), text))];
        if self.phase.watches_workspace() {
            self.ws.refresh(&self.p.session_dir);
            let status = self.ws.status(&self.p.session_dir);
            self.p.recorder.event("workspace", json!({"status": status}))?;
            blocks.push(Block::Text(status));
        }
        if screenshot && self.p.cfg.claude.screenshots {
            let path = self.p.recorder.screenshot_path();
            match kit::screenshot(&path, self.p.cfg.claude.screenshot_width) {
                Ok(bytes) => {
                    blocks.push(Block::Text("[screenshot of the candidate's screen attached]".into()));
                    blocks.push(Block::Jpeg(bytes));
                    self.p.recorder.event("screenshot", json!({"file": path.file_name().map(|f| f.to_string_lossy().to_string())}))?;
                }
                Err(e) => self.emit(Output::Status(format!("screenshot failed: {e:#}"))),
            }
        }
        self.emit(Output::Thinking(true));
        let tx = self.tx.clone();
        let result = self.p.claude.turn(blocks, |d| {
            let _ = tx.send(Output::Delta(d.to_string()));
        });
        let result = result.await;
        self.emit(Output::Thinking(false));
        let reply = result?;
        self.cost += reply.cost_usd;
        self.last_interviewer = Instant::now();
        let (spoken, notes, control) = split_reply(&reply.text);
        if !spoken.is_empty() {
            self.p.recorder.say("interviewer", self.phase.key(), &spoken)?;
            self.emit(Output::Interviewer(spoken));
        }
        if !notes.is_empty() {
            self.p.recorder.note(self.phase.key(), &notes)?;
        }
        if let Some(c) = control {
            self.p.recorder.event("control", c.clone())?;
            if let Some(level) = c["hint"].as_u64() {
                let allowed = self.hint_allowed();
                self.hints.push((Instant::now(), level.min(3) as u8));
                self.p.recorder.event("hint", json!({"level": level, "was_allowed": allowed.is_some_and(|a| level as u8 <= a)}))?;
            }
            if c["end"].as_bool() == Some(true) {
                self.ended = true;
            }
            if c["phase_done"].as_bool() == Some(true) && !self.ended {
                self.advance(false).await?;
            }
            if c["look"].as_bool() == Some(true) && !self.ended {
                Box::pin(self.turn("[event] Here is their screen and workspace now.".into(), true)).await?;
            }
        }
        Ok(())
    }

    async fn advance(&mut self, announce: bool) -> Result<()> {
        let Some(next) = self.phase.next() else {
            self.ended = true;
            return Ok(());
        };
        self.set_phase(next)?;
        let reason = if announce { "Time is up for the previous phase." } else { "You marked the previous phase as done." };
        let text = format!("[event] Phase change: {}. {reason} {}", next.key(), next.instruction());
        Box::pin(self.turn(text, false)).await
    }

    async fn candidate(&mut self, said: Vec<String>) -> Result<()> {
        let text = said.join(" ");
        self.last_candidate = Instant::now();
        let wants_look = {
            let t = text.to_lowercase();
            ["screen", "take a look", "can you see", "look at this", "my test", "my code"].iter().any(|k| t.contains(k))
        };
        let screenshot = wants_look && self.phase.watches_workspace();
        self.turn(format!("Candidate: \"{text}\""), screenshot).await
    }

    async fn proactive(&mut self) -> Result<()> {
        if self.activity.busy() || self.last_proactive.elapsed() < Duration::from_secs(60) {
            return Ok(());
        }
        let quiet = self.last_candidate.elapsed().min(self.last_interviewer.elapsed());
        if self.phase_left() <= 0.0 {
            self.last_proactive = Instant::now();
            return self.advance(true).await;
        }
        let elapsed = self.elapsed();
        if elapsed > self.p.minutes * 60.0 + 300.0 {
            self.ended = true;
            return Ok(());
        }
        if !matches!(self.phase, Phase::Setup | Phase::Coding) {
            return Ok(());
        }
        if self.ws.last_checked.elapsed() > Duration::from_secs(20) && self.ws.refresh(&self.p.session_dir) {
            self.p.recorder.event("tests", json!({"summary": self.ws.last_tests.summary()}))?;
        }
        let silence = Duration::from_secs(self.p.cfg.interview.silence_prompt_seconds as u64);
        let check_in = Duration::from_secs(self.p.cfg.interview.check_in_minutes as u64 * 60);
        let no_tests = Duration::from_secs(self.p.cfg.interview.no_test_change_minutes as u64 * 60);
        let reason = if self.last_check_in.elapsed() >= check_in {
            Some("Scheduled check-in. Look at their screen and progress and react naturally.".to_string())
        } else if self.phase == Phase::Coding && !self.nudged_tests && self.ws.last_test_change.elapsed() >= no_tests {
            self.nudged_tests = true;
            Some(format!(
                "They haven't changed any test files for {} minutes. If it fits what they're doing, nudge them toward proving their hypothesis with a test.",
                no_tests.as_secs() / 60
            ))
        } else if quiet >= silence {
            Some(format!("The candidate has been quiet for {} seconds. Prompt them to think out loud.", quiet.as_secs()))
        } else {
            None
        };
        if let Some(reason) = reason {
            self.last_proactive = Instant::now();
            self.last_check_in = Instant::now();
            self.p.recorder.event("check_in", json!({"reason": reason}))?;
            self.turn(format!("[event] {reason}"), true).await?;
        }
        Ok(())
    }

    async fn finish(&mut self) -> Result<()> {
        let dir = self.p.recorder.dir.clone();
        let session = self.p.session_dir.clone();
        self.p.claude.close().await;
        std::fs::write(dir.join("diff.patch"), kit::diff(&session).unwrap_or_default())?;
        std::fs::write(dir.join("grade.txt"), kit::grade(&self.p.cfg.kit(), &self.p.exercise, &session).unwrap_or_default())?;
        let meta_path = dir.join("meta.json");
        if let Ok(text) = std::fs::read_to_string(&meta_path) {
            if let Ok(mut meta) = serde_json::from_str::<serde_json::Value>(&text) {
                meta["ended"] = json!(chrono::Local::now().to_rfc3339());
                meta["elapsed_seconds"] = json!(self.elapsed());
                meta["claude_cost_equivalent_usd"] = json!(self.cost);
                std::fs::write(&meta_path, serde_json::to_string_pretty(&meta)?)?;
            }
        }
        self.p.recorder.event("end", json!({}))?;
        Ok(())
    }
}

pub async fn run(p: Prepared, mut rx: UnboundedReceiver<Input>, tx: UnboundedSender<Output>, activity: Arc<dyn Activity>) -> Result<PathBuf> {
    let now = Instant::now();
    let long_ago = now.checked_sub(Duration::from_secs(3600)).unwrap_or(now);
    let mut core = Core {
        p,
        tx,
        activity,
        started: now,
        phase: Phase::Greeting,
        phase_started: now,
        last_candidate: now,
        last_interviewer: now,
        last_proactive: now,
        last_check_in: now,
        nudged_tests: false,
        hints: Vec::new(),
        ws: Workspace { last_mtime: None, last_tests: TestRun::default(), last_test_change: now, last_checked: long_ago },
        ended: false,
        cost: 0.0,
    };
    core.set_phase(Phase::Greeting)?;
    core.turn("[event] The candidate has joined the video call. Begin with the greeting.".into(), false).await?;
    let mut ticker = tokio::time::interval(Duration::from_millis(500));
    while !core.ended {
        tokio::select! {
            input = rx.recv() => {
                let Some(input) = input else { break };
                let mut said = Vec::new();
                let mut queue = vec![input];
                while let Ok(more) = rx.try_recv() {
                    queue.push(more);
                }
                for i in queue {
                    match i {
                        Input::Said(t) => {
                            core.p.recorder.say("candidate", core.phase.key(), &t)?;
                            core.emit(Output::Candidate(t.clone()));
                            said.push(t);
                        }
                        Input::NextPhase => core.advance(true).await?,
                        Input::Look => core.turn("[event] The candidate wants you to look at their screen.".into(), true).await?,
                        Input::End => core.ended = true,
                    }
                }
                if !said.is_empty() && !core.ended {
                    core.candidate(said).await?;
                }
            }
            _ = ticker.tick() => {
                if !core.activity.busy() {
                    core.proactive().await?;
                }
            }
        }
    }
    core.finish().await?;
    let dir = core.p.recorder.dir.clone();
    core.emit(Output::Ended);
    Ok(dir)
}
