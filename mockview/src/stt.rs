use std::path::Path;

use anyhow::{anyhow, Result};
use whisper_rs::{FullParams, SamplingStrategy, WhisperContext, WhisperContextParameters, WhisperState};

pub struct Stt {
    state: WhisperState,
    threads: i32,
    pub prompt: String,
}

/// "auto" picks the most accurate model that's downloaded (large-v3-turbo 8-bit, then 5-bit, then small.en).
pub fn choose_model(configured: &str) -> String {
    if configured != "auto" {
        return configured.to_string();
    }
    let dir = crate::config::Config::models_dir();
    ["ggml-large-v3-turbo-q8_0.bin", "ggml-large-v3-turbo-q5_0.bin", "ggml-small.en.bin"]
        .into_iter()
        .find(|m| dir.join(m).exists())
        .unwrap_or("ggml-large-v3-turbo-q8_0.bin")
        .to_string()
}

pub const BASE_VOCAB: &str = "A software engineering interview at Bloomberg. We talked about the spec, unit tests, a deque, \
a heap, a hash map, binary search, time complexity, idempotency, a race condition, edge cases, the invariant, the test failure, \
my AI assistant, Python, Rust, TypeScript, PostgreSQL and Redis.";

impl Stt {
    pub fn load(model: &Path, threads: i32) -> Result<Self> {
        whisper_rs::install_logging_hooks();
        let mut ctx_params = WhisperContextParameters::default();
        ctx_params.flash_attn(true);
        let ctx = WhisperContext::new_with_params(model.to_str().unwrap(), ctx_params)
            .map_err(|e| anyhow!("loading whisper model {}: {e}", model.display()))?;
        let state = ctx.create_state().map_err(|e| anyhow!("{e}"))?;
        Box::leak(Box::new(ctx));
        Ok(Self { state, threads, prompt: BASE_VOCAB.to_string() })
    }

    /// Has this audio got enough energy to be worth transcribing (skips trailing silence)?
    pub fn worth_it(audio: &[f32]) -> bool {
        if audio.len() < 8_000 {
            return false;
        }
        let peak = audio.chunks(1_600).map(|c| (c.iter().map(|x| x * x).sum::<f32>() / c.len() as f32).sqrt()).fold(0.0, f32::max);
        peak > 0.004
    }

    pub fn transcribe(&mut self, audio: &[f32]) -> Result<String> {
        if audio.len() < 8_000 {
            return Ok(String::new());
        }
        let mut padded;
        let audio = if audio.len() < 16_000 + 1_600 {
            padded = audio.to_vec();
            padded.resize(16_000 + 1_600, 0.0);
            &padded[..]
        } else {
            audio
        };
        let mut params = FullParams::new(SamplingStrategy::Greedy { best_of: 1 });
        params.set_language(Some("en"));
        params.set_n_threads(self.threads);
        params.set_print_progress(false);
        params.set_print_realtime(false);
        params.set_print_timestamps(false);
        params.set_print_special(false);
        params.set_no_context(true);
        params.set_suppress_blank(true);
        params.set_initial_prompt(&self.prompt);
        params.set_suppress_nst(true);
        params.set_temperature(0.0);
        params.set_temperature_inc(0.2);
        params.set_entropy_thold(2.4);
        params.set_logprob_thold(-1.0);
        params.set_no_speech_thold(0.6);
        let seconds = audio.len() as f64 / 16_000.0;
        params.set_max_tokens((seconds * 6.0) as i32 + 24);
        if seconds < 25.0 {
            params.set_audio_ctx(((seconds / 30.0 * 1500.0).ceil() as i32 + 256).clamp(512, 1500));
        }
        self.state.full(params, audio).map_err(|e| anyhow!("whisper: {e}"))?;
        let mut text = String::new();
        for i in 0..self.state.full_n_segments() {
            if let Some(seg) = self.state.get_segment(i) {
                text.push_str(&seg.to_str_lossy().map_err(|e| anyhow!("{e}"))?);
            }
        }
        Ok(clean(&text))
    }
}

/// Collapse whisper repetition loops ("make, make, make, …", "O(1) O(1) O(1)").
pub fn squash_repeats(text: &str) -> String {
    let words: Vec<&str> = text.split_whitespace().collect();
    let norm = |w: &str| w.trim_matches(|c: char| !c.is_alphanumeric()).to_lowercase();
    let mut out: Vec<&str> = Vec::new();
    let mut i = 0;
    'outer: while i < words.len() {
        for n in 1..=4 {
            if i + n * 3 > words.len() {
                break;
            }
            let gram: Vec<String> = words[i..i + n].iter().map(|w| norm(w)).collect();
            let mut reps = 1;
            while i + n * (reps + 1) <= words.len()
                && words[i + n * reps..i + n * (reps + 1)].iter().map(|w| norm(w)).collect::<Vec<_>>() == gram
            {
                reps += 1;
            }
            if reps >= 3 {
                out.extend_from_slice(&words[i..i + n]);
                i += n * reps;
                continue 'outer;
            }
        }
        out.push(words[i]);
        i += 1;
    }
    out.join(" ")
}

fn clean(text: &str) -> String {
    let t = text.trim();
    let noise = ["[BLANK_AUDIO]", "(silence)", "[ Silence ]", "[MUSIC]", "(music)", "Thank you.", "Thanks for watching!"];
    if noise.iter().any(|n| t.eq_ignore_ascii_case(n)) {
        return String::new();
    }
    let t = t.replace("[BLANK_AUDIO]", "");
    let t = t.trim().trim_start_matches(['-', '–', '—', ' ']).to_string();
    if !t.chars().any(char::is_alphanumeric) {
        return String::new();
    }
    squash_repeats(t.trim())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn squashes_loops() {
        assert_eq!(squash_repeats("Okay make, make, make, make, make, make done"), "Okay make, done");
        assert_eq!(squash_repeats("test_orderbook, test_orderbook, test_orderbook, And from the failure"), "test_orderbook, And from the failure");
        assert_eq!(squash_repeats("Good. Good. Good. Good. O(1) O(1) O(1)"), "Good. O(1)");
        assert_eq!(squash_repeats("I think I think it works"), "I think I think it works");
    }
}
