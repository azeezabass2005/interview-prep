use anyhow::{anyhow, Result};
use ort::session::Session;
use ort::value::Tensor;

use crate::config::Config;

const FRAME: usize = 512;
const CONTEXT: usize = 64;
const FRAME_MS: u32 = 32;

pub struct Silero {
    session: Session,
    state: Vec<f32>,
    context: Vec<f32>,
}

impl Silero {
    pub fn load() -> Result<Self> {
        let session = crate::onnx::session(&Config::models_dir().join("silero_vad.onnx"), 1)?;
        Ok(Self { session, state: vec![0.0; 2 * 128], context: vec![0.0; CONTEXT] })
    }

    pub fn reset(&mut self) {
        self.state.iter_mut().for_each(|x| *x = 0.0);
        self.context.iter_mut().for_each(|x| *x = 0.0);
    }

    pub fn prob(&mut self, frame: &[f32]) -> Result<f32> {
        let mut input = Vec::with_capacity(CONTEXT + FRAME);
        input.extend_from_slice(&self.context);
        input.extend_from_slice(frame);
        self.context.copy_from_slice(&frame[FRAME - CONTEXT..]);
        let outputs = self
            .session
            .run(ort::inputs![
                "input" => Tensor::from_array(([1usize, CONTEXT + FRAME], input))?,
                "state" => Tensor::from_array(([2usize, 1, 128], self.state.clone()))?,
                "sr" => Tensor::from_array(((), vec![16_000i64]))?,
            ])
            .map_err(|e| anyhow!("vad: {e}"))?;
        let (_, p) = outputs["output"].try_extract_tensor::<f32>()?;
        let p = p[0];
        let (_, s) = outputs["stateN"].try_extract_tensor::<f32>()?;
        self.state.copy_from_slice(s);
        Ok(p)
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum VadEvent {
    SpeechStart,
    Silence,
}

/// Audio handed to speech recognition: a piece cut at a pause while you keep talking, or the end of your turn.
pub enum Piece {
    Segment(Vec<f32>),
    End(Vec<f32>),
    Discard,
}

const SEGMENT_PAUSE_MS: u32 = 300;
const MIN_SEGMENT: usize = 16_000 * 3;

/// Turns a stream of 16 kHz samples into finished utterances.
pub struct Endpointer {
    vad: Silero,
    pending: Vec<f32>,
    preroll: Vec<f32>,
    utterance: Vec<f32>,
    in_speech: bool,
    speech_frames: u32,
    since_cut: u32,
    silence_ms: u32,
    hot_frames: u32,
    pub endpoint_ms: u32,
    pub hold: bool,
    pub last_prob: f32,
}

impl Endpointer {
    pub fn new(endpoint_ms: u32) -> Result<Self> {
        Ok(Self {
            vad: Silero::load()?,
            pending: Vec::new(),
            preroll: Vec::new(),
            utterance: Vec::new(),
            in_speech: false,
            speech_frames: 0,
            since_cut: 0,
            silence_ms: 0,
            hot_frames: 0,
            endpoint_ms,
            hold: false,
            last_prob: 0.0,
        })
    }

    pub fn in_speech(&self) -> bool {
        self.in_speech
    }

    /// Feed audio; returns pieces ready for speech recognition.
    pub fn push_pieces(&mut self, samples: &[f32], mut on_event: impl FnMut(VadEvent)) -> Result<Vec<Piece>> {
        self.pending.extend_from_slice(samples);
        let mut out = Vec::new();
        while self.pending.len() >= FRAME {
            let frame: Vec<f32> = self.pending.drain(..FRAME).collect();
            let p = self.vad.prob(&frame)?;
            self.last_prob = p;
            if !self.in_speech {
                self.preroll.extend_from_slice(&frame);
                let keep = FRAME * 10;
                if self.preroll.len() > keep {
                    self.preroll.drain(..self.preroll.len() - keep);
                }
                self.hot_frames = if p > 0.5 || self.hold { self.hot_frames + 1 } else { 0 };
                if self.hot_frames >= 2 {
                    self.in_speech = true;
                    self.utterance = std::mem::take(&mut self.preroll);
                    self.speech_frames = 2;
                    self.since_cut = 2;
                    self.silence_ms = 0;
                    on_event(VadEvent::SpeechStart);
                }
                continue;
            }
            self.utterance.extend_from_slice(&frame);
            if p > 0.35 || self.hold {
                self.speech_frames += 1;
                self.since_cut += 1;
                self.silence_ms = 0;
            } else {
                self.silence_ms += FRAME_MS;
            }
            let just_paused = self.silence_ms >= SEGMENT_PAUSE_MS && self.silence_ms < SEGMENT_PAUSE_MS + FRAME_MS;
            if (just_paused && self.utterance.len() >= MIN_SEGMENT) || self.utterance.len() > 16_000 * 60 {
                out.push(Piece::Segment(std::mem::take(&mut self.utterance)));
                self.since_cut = 0;
            }
            if !self.hold && self.silence_ms >= self.endpoint_ms {
                self.in_speech = false;
                on_event(VadEvent::Silence);
                let mut rest = std::mem::take(&mut self.utterance);
                if self.since_cut * FRAME_MS < 250 {
                    rest.clear();
                }
                out.push(if self.speech_frames * FRAME_MS >= 400 { Piece::End(rest) } else { Piece::Discard });
                self.speech_frames = 0;
                self.vad.reset();
            }
        }
        Ok(out)
    }

    /// Force-finish the current utterance (push-to-talk release).
    pub fn flush(&mut self) -> Option<Vec<f32>> {
        if !self.in_speech {
            return None;
        }
        self.in_speech = false;
        self.speech_frames = 0;
        self.vad.reset();
        Some(std::mem::take(&mut self.utterance))
    }
}
