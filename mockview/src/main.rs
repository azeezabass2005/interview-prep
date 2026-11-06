mod audio;
mod claude;
mod config;
mod debrief;
mod interview;
mod keys;
mod kit;
mod layout;
mod onnx;
mod pyenv;
mod record;
mod stt;
mod tts;
mod ui;
mod vad;

use std::path::PathBuf;
use std::time::{Duration, Instant};

use anyhow::{bail, Result};
use clap::{Parser, Subcommand};

use config::Config;

#[derive(Parser)]
#[command(name = "mockview", about = "Voice mock interviewer for the Bloomberg AI-assisted coding rounds")]
struct Cli {
    /// Path to mockview.toml (default: found from the current directory)
    #[arg(long, global = true)]
    config: Option<PathBuf>,
    #[command(subcommand)]
    command: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    /// Run a full mock interview
    Interview {
        /// Exercise to use, e.g. r1/31 or r2/05 (default: random from the pool, preferring ones you haven't done)
        #[arg(long)]
        exercise: Option<String>,
        /// Interviewer persona (part of the name)
        #[arg(long)]
        persona: Option<String>,
        /// Interview length in minutes (phases scale with it)
        #[arg(long)]
        minutes: Option<f64>,
        /// Type instead of talking (no audio)
        #[arg(long)]
        text: bool,
        /// Skip the written debrief at the end
        #[arg(long)]
        no_debrief: bool,
    },
    /// (Re)write the debrief for a finished interview
    Debrief { run: PathBuf },
    /// Scores and trends across your interviews
    Progress,
    /// Check models, audio, Claude Code and tools
    Check,
    /// Test the microphone and speech recognition (or transcribe a WAV file)
    Listen {
        #[arg(long)]
        file: Option<PathBuf>,
    },
    /// Test the interviewer voice
    Say {
        text: String,
        #[arg(long)]
        voice: Option<String>,
        /// Write a WAV file instead of playing it
        #[arg(long)]
        out: Option<PathBuf>,
    },
    /// List the exercises in the pool
    Exercises,
    /// Write the interviewer's answer keys for practice packs (bugs, PM answers, verified fixes and hidden tests)
    Keys {
        /// One pack, e.g. r1/halcyon (default: every pack in the pool that has no key yet)
        #[arg(long)]
        exercise: Option<String>,
        /// Rewrite keys that already exist
        #[arg(long)]
        force: bool,
    },
    /// List interviewer personas
    Personas,
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();
    let cfg = Config::load(cli.config.as_deref())?;
    let log_dir = cfg.root.join("runs");
    std::fs::create_dir_all(&log_dir)?;
    let log_file = std::fs::OpenOptions::new().create(true).append(true).open(log_dir.join("mockview.log"))?;
    tracing_subscriber::fmt()
        .with_writer(std::sync::Mutex::new(log_file))
        .with_ansi(false)
        .with_env_filter(tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| "mockview=info".into()))
        .init();

    match cli.command {
        Cmd::Interview { exercise, persona, minutes, text, no_debrief } => {
            let ex = interview::choose_exercise(&cfg, exercise.as_deref())?;
            keys::ensure(&cfg, &ex, |m| println!("{m}")).await?;
            let prepared = interview::prepare(&cfg, ex, persona.as_deref(), minutes)?;
            let (run, speaker) = if text {
                (ui::text_mode(prepared).await?, None)
            } else {
                ui::voice_mode(&cfg, prepared).await?
            };
            println!("\nInterview saved in {}", run.display());
            if no_debrief {
                return Ok(());
            }
            println!("Writing your debrief (about 3–5 minutes)…");
            let d = debrief::write(&cfg, &run, |m| println!("  {m}")).await?;
            if let Some(s) = &d.scores {
                debrief::print_summary(s);
            }
            println!("\nFull debrief: {}", d.report.display());
            open_report(&cfg, &d.report);
            if let (Some(tx), Some(summary)) = (speaker, d.spoken_summary.clone()) {
                println!("\n{summary}\n");
                let _ = tx.send(summary);
                tokio::time::sleep(Duration::from_secs(2)).await;
                drop(tx);
                tokio::time::sleep(Duration::from_secs(60)).await;
            } else if let Some(summary) = d.spoken_summary {
                println!("\n{summary}");
            }
        }
        Cmd::Debrief { run } => {
            let run = if run.is_absolute() || run.exists() { run } else { cfg.runs_dir().join(run) };
            let d = debrief::write(&cfg, &run, |m| println!("  {m}")).await?;
            if let Some(s) = &d.scores {
                debrief::print_summary(s);
            }
            println!("\nFull debrief: {}", d.report.display());
            open_report(&cfg, &d.report);
        }
        Cmd::Progress => debrief::progress(&cfg)?,
        Cmd::Check => check(&cfg).await?,
        Cmd::Listen { file } => listen(&cfg, file)?,
        Cmd::Say { text, voice, out } => say(&cfg, &text, voice, out)?,
        Cmd::Exercises => {
            for e in kit::list(&cfg.kit(), &cfg.interview.exercise_pool)? {
                let key = if !e.pack { "" } else if keys::ready(&cfg, &e) { "answer key ready" } else { "no answer key yet" };
                println!("r{}/{:<32} {:<34} {}", e.round, e.name, e.title(), key);
            }
        }
        Cmd::Keys { exercise, force } => {
            let list = match exercise {
                Some(spec) => vec![kit::resolve(&cfg.kit(), &spec)?],
                None => kit::list(&cfg.kit(), &cfg.interview.exercise_pool)?,
            };
            keys::generate_many(&cfg, list, force).await?;
        }
        Cmd::Personas => {
            for p in interview::personas(&cfg)? {
                println!("{:<18} {:<40} {:<9} {}", p.name, p.team, p.office, p.voice);
            }
        }
    }
    Ok(())
}

fn open_report(cfg: &Config, report: &std::path::Path) {
    if cfg.editor.command != "none" && cfg.editor.open_debrief {
        let _ = std::process::Command::new(&cfg.editor.command).arg(report).spawn();
    }
}

fn say(cfg: &Config, text: &str, voice: Option<String>, out: Option<PathBuf>) -> Result<()> {
    let voice = voice.unwrap_or_else(|| if cfg.tts.voice == "auto" { "am_michael".into() } else { cfg.tts.voice.clone() });
    let t0 = Instant::now();
    let mut engine = tts::Kokoro::load(&voice, cfg.tts.speed)?;
    let load = t0.elapsed();
    let t1 = Instant::now();
    let samples = engine.synthesize(&tts::speakable(text))?;
    let synth = t1.elapsed();
    println!(
        "voice {voice}: loaded in {:.1}s, synthesised {:.1}s of audio in {:.2}s",
        load.as_secs_f32(),
        samples.len() as f32 / audio::TTS_RATE as f32,
        synth.as_secs_f32()
    );
    if let Some(path) = out {
        audio::wav_write(&path, &samples, audio::TTS_RATE)?;
        println!("wrote {}", path.display());
        return Ok(());
    }
    let a = audio::start(None, true)?;
    a.shared.play(&samples);
    std::thread::sleep(Duration::from_millis(300));
    while a.shared.speaking() {
        std::thread::sleep(Duration::from_millis(100));
    }
    Ok(())
}

fn listen(cfg: &Config, file: Option<PathBuf>) -> Result<()> {
    let t0 = Instant::now();
    let model = stt::choose_model(&cfg.stt.model);
    let mut stt = stt::Stt::load(&Config::models_dir().join(&model), cfg.stt.threads)?;
    println!("{model} loaded in {:.1}s", t0.elapsed().as_secs_f32());
    if let Some(f) = file {
        let mut samples = audio::wav_read_16k(&f)?;
        samples.extend(std::iter::repeat_n(0.0, 16_000 * 2));
        let mut ep = vad::Endpointer::new(cfg.audio.endpoint_silence_ms)?;
        let mut heard = Vec::new();
        for (i, chunk) in samples.chunks(1_600).enumerate() {
            for piece in ep.push_pieces(chunk, |_| {})? {
                let at = i as f32 * 0.1;
                let (audio, end) = match piece {
                    vad::Piece::Segment(a) => (a, false),
                    vad::Piece::End(a) => (a, true),
                    vad::Piece::Discard => continue,
                };
                let t1 = Instant::now();
                let text = if stt::Stt::worth_it(&audio) { stt.transcribe(&audio)? } else { String::new() };
                println!(
                    "  {} at {at:.1}s: {:.1}s of audio transcribed in {:.2}s: {text}",
                    if end { "end    " } else { "segment" },
                    audio.len() as f32 / 16_000.0,
                    t1.elapsed().as_secs_f32()
                );
                heard.push(text);
            }
        }
        println!("Result: {}", heard.join(" ").trim());
        return Ok(());
    }
    let (tx, rx) = std::sync::mpsc::channel();
    let _audio = audio::start(Some(tx), false)?;
    let mut ep = vad::Endpointer::new(cfg.audio.endpoint_silence_ms)?;
    println!("Listening. Speak, pause, and your words appear. Ctrl+C to stop.");
    let mut heard = Vec::new();
    let mut seconds = 0.0;
    loop {
        let chunk = rx.recv()?;
        for piece in ep.push_pieces(&chunk, |_| {})? {
            let (audio, end) = match piece {
                vad::Piece::Segment(a) => (a, false),
                vad::Piece::End(a) => (a, true),
                vad::Piece::Discard => {
                    heard.clear();
                    continue;
                }
            };
            seconds += audio.len() as f32 / 16_000.0;
            let t1 = Instant::now();
            if stt::Stt::worth_it(&audio) {
                heard.push(stt.transcribe(&audio)?);
            }
            if end {
                println!("[{seconds:.1}s of speech, {:.2}s after you stopped] {}", t1.elapsed().as_secs_f32(), heard.join(" "));
                heard.clear();
                seconds = 0.0;
            }
        }
    }
}

async fn check(cfg: &Config) -> Result<()> {
    let mut ok = true;
    let mut row = |name: &str, good: bool, detail: String| {
        ok &= good;
        println!("{} {:<22} {}", if good { "✓" } else { "✗" }, name, detail);
    };
    let models = Config::models_dir();
    let stt_model = stt::choose_model(&cfg.stt.model);
    for f in [stt_model.as_str(), "kokoro-v1.0.onnx", "voices-v1.0.bin", "kokoro-config.json", "silero_vad.onnx"] {
        let p = models.join(f);
        let size = p.metadata().map(|m| m.len()).unwrap_or(0);
        row(f, size > 0, format!("{} MB", size / 1_000_000));
    }
    for (tool, arg) in [("espeak-ng", "--version"), ("grim", "-h"), ("ffmpeg", "-version"), ("pdftotext", "-v"), ("zeditor", "--version"), ("git", "--version"), ("python3", "--version")] {
        let found = std::process::Command::new(tool).arg(arg).output().is_ok();
        row(tool, found, if found { "found".into() } else { "missing".into() });
    }
    let kit_dir = cfg.kit();
    let exercises = kit::list(&kit_dir, &cfg.interview.exercise_pool).unwrap_or_default();
    if kit::is_mock_kit(&kit_dir) {
        row("interview kit", !exercises.is_empty(), format!("{} ({} exercises)", kit_dir.display(), exercises.len()));
    } else {
        let keyed = exercises.iter().filter(|e| keys::ready(cfg, e)).count();
        row("practice packs", !exercises.is_empty(), format!("{} ({} packs, Python)", kit_dir.display(), exercises.len()));
        match pyenv::python() {
            Ok(py) => row("pytest", true, py.display().to_string()),
            Err(e) => row("pytest", false, format!("{e:#}")),
        }
        row("answer keys", true, format!("{keyed}/{} ready (missing ones are written before an interview, or run `mockview keys`)", exercises.len()));
    }
    row(
        "resume",
        interview::resume_text(cfg).is_some(),
        if interview::resume_text(cfg).is_some() { "found".into() } else { format!("none yet: put resume.pdf or resume.md in {}", cfg.resume_dir().display()) },
    );
    match audio::start(Some(std::sync::mpsc::channel().0), true) {
        Ok(a) => {
            std::thread::sleep(Duration::from_millis(800));
            row("audio", true, format!("mic and speakers open (mic level {:.4})", a.shared.mic_level()));
        }
        Err(e) => row("audio", false, format!("{e:#}")),
    }
    let t0 = Instant::now();
    match claude::oneshot("Reply with exactly: ready", "You are a test.", &cfg.root, &[], &[], &cfg.claude.model).await {
        Ok(r) => row("claude code", r.to_lowercase().contains("ready"), format!("answered in {:.1}s using your Claude login", t0.elapsed().as_secs_f32())),
        Err(e) => row("claude code", false, format!("{e:#}")),
    }
    if !ok {
        bail!("some checks failed");
    }
    println!("\nAll good.");
    Ok(())
}
