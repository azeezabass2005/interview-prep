use std::path::PathBuf;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

use anyhow::{anyhow, Result};
use crossterm::event::{self, Event, KeyCode, KeyEventKind};
use ratatui::layout::{Constraint, Layout};
use ratatui::style::{Color, Modifier, Style, Stylize};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Gauge, Paragraph, Wrap};
use tokio::io::AsyncBufReadExt;
use tokio::sync::mpsc::{unbounded_channel, UnboundedSender};

use crate::audio::{self, Shared};
use crate::config::Config;
use crate::interview::{self, Activity, Input, NoActivity, Output, Phase, Prepared};
use crate::record::mmss;
use crate::stt::{Stt, BASE_VOCAB};
use crate::tts::{self, split_reply, SentenceSplitter, TtsCmd};
use crate::vad::{Endpointer, Piece, VadEvent};

pub async fn text_mode(p: Prepared) -> Result<PathBuf> {
    let name = p.persona.name.split_whitespace().next().unwrap_or("Interviewer").to_string();
    println!(
        "Mock interview (text mode): {} with {} ({}). Exercise: {}\nSession folder (open this in Zed when asked): {}\nType your answers. Commands: /next  /look  /end\n",
        p.exercise.title(),
        p.persona.name,
        p.persona.team,
        p.exercise.id(),
        p.session_dir.display()
    );
    let (in_tx, in_rx) = unbounded_channel();
    let (out_tx, mut out_rx) = unbounded_channel();
    let core = tokio::spawn(interview::run(p, in_rx, out_tx, Arc::new(NoActivity)));
    tokio::spawn(async move {
        let mut lines = tokio::io::BufReader::new(tokio::io::stdin()).lines();
        while let Ok(Some(line)) = lines.next_line().await {
            let line = line.trim().to_string();
            let input = match line.as_str() {
                "" => continue,
                "/next" => Input::NextPhase,
                "/look" => Input::Look,
                "/end" => Input::End,
                _ => Input::Said(line),
            };
            if in_tx.send(input).is_err() {
                break;
            }
        }
    });
    while let Some(o) = out_rx.recv().await {
        match o {
            Output::Interviewer(t) => println!("\n{name}: {t}\n"),
            Output::Phase(ph, secs) => println!("--- {} ({}) ---", ph.label(), mmss(secs)),
            Output::Status(s) => println!("[{s}]"),
            Output::Ended => break,
            _ => {}
        }
    }
    core.await.map_err(|e| anyhow!("{e}"))?
}

#[derive(Clone, Copy, PartialEq)]
enum Ear {
    Loading,
    Listening,
    Hearing,
    Transcribing,
    Muted,
}

struct Ui {
    lines: Vec<(f64, String, String)>,
    streaming: String,
    phase: Phase,
    phase_budget: f64,
    phase_started: Instant,
    started: Instant,
    minutes: f64,
    status: String,
    thinking: bool,
    ear: Ear,
    hold: bool,
    confirm_quit: bool,
    title: String,
    persona: String,
    voice: String,
    stt_model: String,
}

struct VoiceActivity {
    shared: Arc<Shared>,
    hearing: Arc<AtomicBool>,
}

impl Activity for VoiceActivity {
    fn busy(&self) -> bool {
        self.shared.speaking() || self.hearing.load(Ordering::Relaxed)
    }
}

pub async fn voice_mode(cfg: &Config, p: Prepared) -> Result<(PathBuf, Option<UnboundedSender<String>>)> {
    let run_dir = p.recorder.dir.clone();
    let prompt = format!("{BASE_VOCAB} The interviewer is {}.", p.persona.name);
    let ui = Arc::new(Mutex::new(Ui {
        lines: Vec::new(),
        streaming: String::new(),
        phase: Phase::Greeting,
        phase_budget: 0.0,
        phase_started: Instant::now(),
        started: Instant::now(),
        minutes: p.minutes,
        status: "loading speech models…".into(),
        thinking: false,
        ear: Ear::Loading,
        hold: false,
        confirm_quit: false,
        title: format!("{} ({})", p.exercise.title(), p.exercise.id()),
        persona: format!("{}, {}", p.persona.name, p.persona.team),
        voice: p.voice(),
        stt_model: crate::stt::choose_model(&cfg.stt.model).trim_start_matches("ggml-").trim_end_matches(".bin").to_string(),
    }));

    let (mic_tx, mic_rx) = std::sync::mpsc::channel::<Vec<f32>>();
    let audio = audio::start(Some(mic_tx), true)?;
    let shared = audio.shared.clone();
    let tts_tx = tts::spawn(p.voice(), cfg.tts.speed, shared.clone())?;

    let (in_tx, in_rx) = unbounded_channel::<Input>();
    let hearing = Arc::new(AtomicBool::new(false));
    let hold = Arc::new(AtomicBool::new(false));
    {
        let model = Config::models_dir().join(crate::stt::choose_model(&cfg.stt.model));
        let threads = cfg.stt.threads;
        let endpoint = cfg.audio.endpoint_silence_ms;
        let record_audio = cfg.audio.record_audio.then(|| run_dir.join("audio"));
        let (ui, in_tx, hearing, hold, shared) = (ui.clone(), in_tx.clone(), hearing.clone(), hold.clone(), shared.clone());
        std::thread::spawn(move || {
            let result = (|| -> Result<()> {
                let mut stt = Stt::load(&model, threads)?;
                stt.prompt = prompt;
                let mut ep = Endpointer::new(endpoint)?;
                ui.lock().unwrap().ear = Ear::Listening;
                ui.lock().unwrap().status.clear();
                let mut n = 0;
                let mut heard: Vec<String> = Vec::new();
                loop {
                    let chunk = match mic_rx.recv_timeout(Duration::from_millis(100)) {
                        Ok(c) => c,
                        Err(std::sync::mpsc::RecvTimeoutError::Timeout) => Vec::new(),
                        Err(_) => break,
                    };
                    let holding = hold.load(Ordering::Relaxed);
                    let mut pieces = Vec::new();
                    if ep.hold && !holding {
                        ep.hold = false;
                        if let Some(rest) = ep.flush() {
                            pieces.push(Piece::End(rest));
                        }
                    }
                    ep.hold = holding;
                    if !chunk.is_empty() {
                        pieces.extend(ep.push_pieces(&chunk, |e| hearing.store(e == VadEvent::SpeechStart, Ordering::Relaxed))?);
                    }
                    let muted = shared.user_mute.load(Ordering::Relaxed);
                    {
                        let mut u = ui.lock().unwrap();
                        if u.ear != Ear::Transcribing {
                            u.ear = if muted { Ear::Muted } else if ep.in_speech() { Ear::Hearing } else { Ear::Listening };
                        }
                    }
                    for piece in pieces {
                        let (audio, end) = match piece {
                            Piece::Segment(a) => (a, false),
                            Piece::End(a) => (a, true),
                            Piece::Discard => {
                                heard.clear();
                                hearing.store(false, Ordering::Relaxed);
                                continue;
                            }
                        };
                        if let Some(dir) = &record_audio {
                            n += 1;
                            let _ = std::fs::create_dir_all(dir);
                            let _ = audio::wav_write(&dir.join(format!("{n:03}.wav")), &audio, audio::MIC_RATE);
                        }
                        if end {
                            hearing.store(true, Ordering::Relaxed);
                            ui.lock().unwrap().ear = Ear::Transcribing;
                        }
                        if Stt::worth_it(&audio) {
                            let text = stt.transcribe(&audio)?;
                            if !text.is_empty() {
                                heard.push(text);
                            }
                        }
                        if end {
                            ui.lock().unwrap().ear = Ear::Listening;
                            hearing.store(ep.in_speech(), Ordering::Relaxed);
                            let text = heard.join(" ");
                            heard.clear();
                            if !text.trim().is_empty() && in_tx.send(Input::Said(text)).is_err() {
                                return Ok(());
                            }
                        }
                    }
                }
                Ok(())
            })();
            if let Err(e) = result {
                ui.lock().unwrap().status = format!("speech recognition stopped: {e:#}");
            }
        });
    }
    while ui.lock().unwrap().ear == Ear::Loading {
        tokio::time::sleep(Duration::from_millis(100)).await;
        if ui.lock().unwrap().status.starts_with("speech recognition stopped") {
            return Err(anyhow!(ui.lock().unwrap().status.clone()));
        }
    }

    let (out_tx, mut out_rx) = unbounded_channel::<Output>();
    let activity = Arc::new(VoiceActivity { shared: shared.clone(), hearing: hearing.clone() });
    {
        let mut u = ui.lock().unwrap();
        u.started = Instant::now();
        u.phase_started = Instant::now();
    }
    let core = tokio::spawn(interview::run(p, in_rx, out_tx, activity));

    let ended = Arc::new(AtomicBool::new(false));
    {
        let (ui, tts_tx, ended) = (ui.clone(), tts_tx.clone(), ended.clone());
        tokio::spawn(async move {
            let mut splitter = SentenceSplitter::default();
            while let Some(o) = out_rx.recv().await {
                let mut u = ui.lock().unwrap();
                match o {
                    Output::Delta(d) => {
                        u.streaming.push_str(&d);
                        for s in splitter.push(&d) {
                            let _ = tts_tx.send(TtsCmd::Say(s));
                        }
                    }
                    Output::Interviewer(t) => {
                        for s in splitter.finish() {
                            let _ = tts_tx.send(TtsCmd::Say(s));
                        }
                        u.streaming.clear();
                        let t0 = u.started.elapsed().as_secs_f64();
                        let who = u.persona.split_whitespace().next().unwrap_or("").to_string();
                        u.lines.push((t0, who, t));
                    }
                    Output::Candidate(t) => {
                        let t0 = u.started.elapsed().as_secs_f64();
                        u.lines.push((t0, "You".into(), t));
                    }
                    Output::Phase(ph, secs) => {
                        u.phase = ph;
                        u.phase_budget = secs;
                        u.phase_started = Instant::now();
                    }
                    Output::Status(s) => u.status = s,
                    Output::Thinking(b) => {
                        u.thinking = b;
                        if !b {
                            for s in splitter.finish() {
                                let _ = tts_tx.send(TtsCmd::Say(s));
                            }
                            u.streaming.clear();
                        }
                    }
                    Output::Ended => {
                        ended.store(true, Ordering::Relaxed);
                    }
                }
            }
        });
    }

    let mut terminal = ratatui::init();
    let keys = spawn_key_reader();
    let result: Result<()> = loop {
        if ended.load(Ordering::Relaxed) && !shared.speaking() {
            break Ok(());
        }
        terminal.draw(|f| draw(f, &ui.lock().unwrap(), &shared))?;
        while let Ok(code) = keys.try_recv() {
            let mut u = ui.lock().unwrap();
            if u.confirm_quit {
                u.confirm_quit = false;
                if code == KeyCode::Char('y') {
                    let _ = in_tx.send(Input::End);
                    shared.stop_playback();
                    u.status = "ending the interview…".into();
                } else {
                    u.status.clear();
                }
                continue;
            }
            match code {
                KeyCode::Char(' ') => {
                    let h = !hold.load(Ordering::Relaxed);
                    hold.store(h, Ordering::Relaxed);
                    u.hold = h;
                }
                KeyCode::Char('m') => {
                    let m = !shared.user_mute.load(Ordering::Relaxed);
                    shared.user_mute.store(m, Ordering::Relaxed);
                }
                KeyCode::Char('s') => shared.stop_playback(),
                KeyCode::Char('n') => {
                    let _ = in_tx.send(Input::NextPhase);
                }
                KeyCode::Char('l') => {
                    let _ = in_tx.send(Input::Look);
                }
                KeyCode::Char('q') => {
                    u.confirm_quit = true;
                    u.status = "End the interview now? y / n".into();
                }
                _ => {}
            }
        }
        tokio::time::sleep(Duration::from_millis(80)).await;
    };
    ratatui::restore();
    result?;
    let dir = core.await.map_err(|e| anyhow!("{e}"))??;
    let (say_tx, mut say_rx) = unbounded_channel::<String>();
    let shared2 = shared.clone();
    tokio::spawn(async move {
        let _keep = audio;
        while let Some(text) = say_rx.recv().await {
            for s in split_sentences(&text) {
                let _ = tts_tx.send(TtsCmd::Say(s));
            }
            tokio::time::sleep(Duration::from_millis(500)).await;
            while shared2.speaking() {
                tokio::time::sleep(Duration::from_millis(100)).await;
            }
        }
    });
    Ok((dir, Some(say_tx)))
}

fn split_sentences(text: &str) -> Vec<String> {
    let mut s = SentenceSplitter::default();
    let mut out = s.push(text);
    out.extend(s.finish());
    out
}

fn spawn_key_reader() -> std::sync::mpsc::Receiver<KeyCode> {
    let (tx, rx) = std::sync::mpsc::channel();
    std::thread::spawn(move || loop {
        if event::poll(Duration::from_millis(100)).unwrap_or(false) {
            if let Ok(Event::Key(k)) = event::read() {
                if k.kind == KeyEventKind::Press && tx.send(k.code).is_err() {
                    break;
                }
            }
        }
    });
    rx
}

fn draw(f: &mut ratatui::Frame, u: &Ui, shared: &Shared) {
    let [header, gauge, body, status, keys] =
        Layout::vertical([Constraint::Length(1), Constraint::Length(1), Constraint::Min(5), Constraint::Length(1), Constraint::Length(1)])
            .areas(f.area());
    let elapsed = u.started.elapsed().as_secs_f64();
    f.render_widget(
        Paragraph::new(Line::from(vec![
            Span::styled(" mockview ", Style::new().bold().fg(Color::Black).bg(Color::Cyan)),
            Span::raw(format!(" {}  ·  {} ", u.title, u.persona)),
            Span::styled(format!(" {} / {} ", mmss(elapsed), mmss(u.minutes * 60.0)), Style::new().bold()),
        ])),
        header,
    );
    let left = (u.phase_budget - u.phase_started.elapsed().as_secs_f64()).max(0.0);
    let ratio = if u.phase_budget > 0.0 { (1.0 - left / u.phase_budget).clamp(0.0, 1.0) } else { 0.0 };
    f.render_widget(
        Gauge::default()
            .gauge_style(Style::new().fg(Color::Cyan))
            .ratio(ratio)
            .label(format!("{}  ·  {} left in this phase", u.phase.label(), mmss(left))),
        gauge,
    );
    let mut lines: Vec<Line> = Vec::new();
    for (t, who, text) in &u.lines {
        let style = if who == "You" { Style::new().fg(Color::Green) } else { Style::new().fg(Color::Cyan) };
        lines.push(Line::from(vec![
            Span::styled(format!("{} ", mmss(*t)), Style::new().fg(Color::DarkGray)),
            Span::styled(format!("{who}: "), style.add_modifier(Modifier::BOLD)),
            Span::raw(text.clone()),
        ]));
        lines.push(Line::raw(""));
    }
    if !u.streaming.is_empty() {
        let (spoken, _, _) = split_reply(&u.streaming);
        let spoken: String = spoken.split('<').next().unwrap_or("").to_string();
        lines.push(Line::from(vec![Span::styled("… ", Style::new().fg(Color::DarkGray)), Span::raw(spoken)]));
    }
    let inner_width = body.width.saturating_sub(2).max(1) as usize;
    let rows: usize = lines.iter().map(|l| (l.width() / inner_width) + 1).sum();
    let visible = body.height.saturating_sub(2) as usize;
    let scroll = rows.saturating_sub(visible) as u16;
    f.render_widget(
        Paragraph::new(lines).wrap(Wrap { trim: false }).scroll((scroll, 0)).block(Block::default().borders(Borders::ALL).title(" Conversation ")),
        body,
    );
    let level = (shared.mic_level() * 400.0).min(8.0) as usize;
    let meter: String = "▁▂▃▄▅▆▇█".chars().take(level.max(1)).collect();
    let (ear_text, ear_color) = if shared.speaking() {
        ("● interviewer speaking", Color::Cyan)
    } else if u.thinking {
        ("● interviewer thinking", Color::Yellow)
    } else {
        match u.ear {
            Ear::Loading => ("● loading", Color::DarkGray),
            Ear::Listening if u.hold => ("● recording (space to finish)", Color::Red),
            Ear::Listening => ("● listening", Color::Green),
            Ear::Hearing => ("● hearing you", Color::Green),
            Ear::Transcribing => ("● transcribing", Color::Yellow),
            Ear::Muted => ("● mic muted", Color::Red),
        }
    };
    let muted = shared.user_mute.load(Ordering::Relaxed);
    f.render_widget(
        Paragraph::new(Line::from(vec![
            Span::styled(format!(" {ear_text} "), Style::new().fg(ear_color).bold()),
            Span::raw(format!(" mic {:<8}", if muted { "muted".to_string() } else { meter })),
            Span::styled(format!(" STT {}  voice {} ", u.stt_model, u.voice), Style::new().fg(Color::DarkGray)),
            Span::styled(u.status.clone(), Style::new().fg(Color::Yellow)),
        ])),
        status,
    );
    f.render_widget(
        Paragraph::new(" [space] hold mic open/close  [m] mute  [s] stop voice  [l] show screen  [n] next phase  [q] end").fg(Color::DarkGray),
        keys,
    );
}
