use std::collections::VecDeque;
use std::sync::atomic::{AtomicBool, AtomicU32, AtomicU64, Ordering};
use std::sync::mpsc::{sync_channel, Sender};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

use anyhow::{anyhow, Context, Result};
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use cpal::{SampleFormat, StreamConfig};

pub const MIC_RATE: u32 = 16_000;
pub const TTS_RATE: u32 = 24_000;
const GATE_TAIL: Duration = Duration::from_millis(350);

pub struct Shared {
    queue: Mutex<VecDeque<f32>>,
    last_play_ms: AtomicU64,
    epoch: Instant,
    pub user_mute: AtomicBool,
    pub level: AtomicU32,
    stop: AtomicBool,
}

impl Shared {
    fn now_ms(&self) -> u64 {
        self.epoch.elapsed().as_millis() as u64
    }

    pub fn speaking(&self) -> bool {
        let busy = !self.queue.lock().unwrap().is_empty();
        busy || self.now_ms().saturating_sub(self.last_play_ms.load(Ordering::Relaxed)) < GATE_TAIL.as_millis() as u64
    }

    pub fn mic_open(&self) -> bool {
        !self.user_mute.load(Ordering::Relaxed) && !self.speaking()
    }

    pub fn play(&self, samples: &[f32]) {
        self.queue.lock().unwrap().extend(samples.iter().copied());
        self.last_play_ms.store(self.now_ms(), Ordering::Relaxed);
    }

    pub fn stop_playback(&self) {
        self.queue.lock().unwrap().clear();
    }

    pub fn mic_level(&self) -> f32 {
        f32::from_bits(self.level.load(Ordering::Relaxed))
    }
}

pub struct Audio {
    pub shared: Arc<Shared>,
    thread: Option<std::thread::JoinHandle<()>>,
}

impl Drop for Audio {
    fn drop(&mut self) {
        self.shared.stop.store(true, Ordering::Relaxed);
        if let Some(t) = self.thread.take() {
            let _ = t.join();
        }
    }
}

/// Starts capture (16 kHz mono chunks sent to `mic_tx` while the mic is open) and/or playback.
pub fn start(capture: Option<Sender<Vec<f32>>>, playback: bool) -> Result<Audio> {
    let shared = Arc::new(Shared {
        queue: Mutex::new(VecDeque::new()),
        last_play_ms: AtomicU64::new(0),
        epoch: Instant::now(),
        user_mute: AtomicBool::new(false),
        level: AtomicU32::new(0),
        stop: AtomicBool::new(false),
    });
    let (ready_tx, ready_rx) = sync_channel::<Result<String>>(1);
    let s = shared.clone();
    let thread = std::thread::spawn(move || {
        let host = cpal::default_host();
        let mut streams = Vec::new();
        let mut info = Vec::new();
        let result = (|| -> Result<()> {
            if let Some(tx) = capture {
                let dev = host.default_input_device().ok_or_else(|| anyhow!("no microphone found"))?;
                let (stream, desc) = build_input(&dev, tx, s.clone())?;
                stream.play()?;
                info.push(desc);
                streams.push(stream);
            }
            if playback {
                let dev = host.default_output_device().ok_or_else(|| anyhow!("no audio output found"))?;
                let (stream, desc) = build_output(&dev, s.clone())?;
                stream.play()?;
                info.push(desc);
                streams.push(stream);
            }
            Ok(())
        })();
        let failed = result.is_err();
        let _ = ready_tx.send(result.map(|_| info.join("; ")));
        if failed {
            return;
        }
        while !s.stop.load(Ordering::Relaxed) {
            std::thread::sleep(Duration::from_millis(50));
        }
        drop(streams);
    });
    let desc = ready_rx.recv().map_err(|_| anyhow!("audio thread died"))??;
    tracing::info!("audio: {desc}");
    Ok(Audio { shared, thread: Some(thread) })
}

fn pick_config(configs: Vec<cpal::SupportedStreamConfigRange>, rate: u32, default: cpal::SupportedStreamConfig) -> (StreamConfig, SampleFormat) {
    let exact = configs
        .iter()
        .filter(|c| c.sample_format() == SampleFormat::F32 && c.min_sample_rate() <= rate && rate <= c.max_sample_rate())
        .min_by_key(|c| c.channels());
    match exact {
        Some(c) => (StreamConfig { channels: c.channels(), sample_rate: rate, buffer_size: cpal::BufferSize::Default }, SampleFormat::F32),
        None => (default.config(), default.sample_format()),
    }
}

fn build_input(dev: &cpal::Device, tx: Sender<Vec<f32>>, shared: Arc<Shared>) -> Result<(cpal::Stream, String)> {
    let configs: Vec<_> = dev.supported_input_configs()?.collect();
    let (config, format) = pick_config(configs, MIC_RATE, dev.default_input_config()?);
    let channels = config.channels as usize;
    let mut resampler = Resampler::new(config.sample_rate, MIC_RATE);
    let desc = format!("mic {} Hz x{} {:?}", config.sample_rate, channels, format);
    let mut handle = move |mono: Vec<f32>| {
        let rms = (mono.iter().map(|x| x * x).sum::<f32>() / mono.len().max(1) as f32).sqrt();
        shared.level.store(rms.to_bits(), Ordering::Relaxed);
        let out = resampler.process(&mono);
        if shared.mic_open() && !out.is_empty() {
            let _ = tx.send(out);
        }
    };
    let err = |e| tracing::error!("mic stream error: {e}");
    let stream = match format {
        SampleFormat::F32 => dev.build_input_stream::<f32, _, _>(config, move |d, _| handle(downmix(d, channels, |x| x)), err, None),
        SampleFormat::I16 => dev.build_input_stream::<i16, _, _>(config, move |d, _| handle(downmix(d, channels, |x| x as f32 / 32768.0)), err, None),
        SampleFormat::I32 => dev.build_input_stream::<i32, _, _>(config, move |d, _| handle(downmix(d, channels, |x| x as f32 / 2147483648.0)), err, None),
        other => return Err(anyhow!("unsupported mic sample format {other:?}")),
    }
    .context("opening microphone")?;
    Ok((stream, desc))
}

fn build_output(dev: &cpal::Device, shared: Arc<Shared>) -> Result<(cpal::Stream, String)> {
    let configs: Vec<_> = dev.supported_output_configs()?.collect();
    let (config, format) = pick_config(configs, TTS_RATE, dev.default_output_config()?);
    let channels = config.channels as usize;
    let step = TTS_RATE as f64 / config.sample_rate as f64;
    let desc = format!("speaker {} Hz x{} {:?}", config.sample_rate, channels, format);
    let mut pos = 0.0f64;
    let mut current = 0.0f32;
    let mut next = 0.0f32;
    let mut fill = move |frames: usize, out: &mut dyn FnMut(usize, f32)| {
        let mut q = shared.queue.lock().unwrap();
        let had = !q.is_empty();
        for i in 0..frames {
            pos += step;
            while pos >= 1.0 {
                pos -= 1.0;
                current = next;
                next = q.pop_front().unwrap_or(0.0);
            }
            out(i, current + (next - current) * pos as f32);
        }
        if had {
            shared.last_play_ms.store(shared.now_ms(), Ordering::Relaxed);
        }
    };
    let err = |e| tracing::error!("speaker stream error: {e}");
    let stream = match format {
        SampleFormat::F32 => dev.build_output_stream::<f32, _, _>(
            config,
            move |d: &mut [f32], _| {
                let frames = d.len() / channels;
                fill(frames, &mut |i, v| d[i * channels..(i + 1) * channels].fill(v));
            },
            err,
            None,
        ),
        SampleFormat::I16 => dev.build_output_stream::<i16, _, _>(
            config,
            move |d: &mut [i16], _| {
                let frames = d.len() / channels;
                fill(frames, &mut |i, v| d[i * channels..(i + 1) * channels].fill((v.clamp(-1.0, 1.0) * 32767.0) as i16));
            },
            err,
            None,
        ),
        other => return Err(anyhow!("unsupported speaker sample format {other:?}")),
    }
    .context("opening speakers")?;
    Ok((stream, desc))
}

fn downmix<T: Copy>(data: &[T], channels: usize, conv: impl Fn(T) -> f32) -> Vec<f32> {
    data.chunks(channels).map(|f| f.iter().map(|&x| conv(x)).sum::<f32>() / channels as f32).collect()
}

/// Box-filter + linear interpolation resampler; good enough for speech going into whisper.
pub struct Resampler {
    ratio: f64,
    pos: f64,
    prev: f32,
    taps: usize,
    history: VecDeque<f32>,
}

impl Resampler {
    pub fn new(from: u32, to: u32) -> Self {
        let ratio = from as f64 / to as f64;
        Self { ratio, pos: 0.0, prev: 0.0, taps: ratio.round().max(1.0) as usize, history: VecDeque::new() }
    }

    pub fn process(&mut self, input: &[f32]) -> Vec<f32> {
        if (self.ratio - 1.0).abs() < 1e-9 {
            return input.to_vec();
        }
        let mut filtered = Vec::with_capacity(input.len());
        for &x in input {
            self.history.push_back(x);
            if self.history.len() > self.taps {
                self.history.pop_front();
            }
            filtered.push(self.history.iter().sum::<f32>() / self.history.len() as f32);
        }
        let mut out = Vec::with_capacity((input.len() as f64 / self.ratio) as usize + 1);
        let mut i = 0usize;
        while i < filtered.len() {
            let cur = filtered[i];
            while self.pos < 1.0 {
                out.push(self.prev + (cur - self.prev) * self.pos as f32);
                self.pos += self.ratio;
            }
            self.pos -= 1.0;
            self.prev = cur;
            i += 1;
        }
        out
    }
}

pub fn wav_write(path: &std::path::Path, samples: &[f32], rate: u32) -> Result<()> {
    let spec = hound::WavSpec { channels: 1, sample_rate: rate, bits_per_sample: 16, sample_format: hound::SampleFormat::Int };
    let mut w = hound::WavWriter::create(path, spec)?;
    for s in samples {
        w.write_sample((s.clamp(-1.0, 1.0) * 32767.0) as i16)?;
    }
    w.finalize()?;
    Ok(())
}

pub fn wav_read_16k(path: &std::path::Path) -> Result<Vec<f32>> {
    let mut r = hound::WavReader::open(path)?;
    let spec = r.spec();
    let raw: Vec<f32> = match spec.sample_format {
        hound::SampleFormat::Int => r.samples::<i32>().map(|s| s.map(|v| v as f32 / (1i64 << (spec.bits_per_sample - 1)) as f32)).collect::<Result<_, _>>()?,
        hound::SampleFormat::Float => r.samples::<f32>().collect::<Result<_, _>>()?,
    };
    let mono = downmix(&raw, spec.channels as usize, |x| x);
    Ok(Resampler::new(spec.sample_rate, MIC_RATE).process(&mono))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn resampler_keeps_duration() {
        let mut r = Resampler::new(48_000, 16_000);
        let out = r.process(&vec![0.5; 48_000]);
        assert!((out.len() as i64 - 16_000).abs() <= 2, "{}", out.len());
        assert!((out[8000] - 0.5).abs() < 1e-3);
    }
}
