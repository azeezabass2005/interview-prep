use std::collections::HashMap;
use std::io::Read;
use std::process::Command;
use std::sync::mpsc::{channel, Sender};
use std::sync::Arc;

use anyhow::{anyhow, bail, Context, Result};
use ort::session::Session;
use ort::value::Tensor;
use regex::Regex;

use crate::audio::Shared;
use crate::config::Config;

pub struct Kokoro {
    session: Session,
    vocab: HashMap<char, i64>,
    style: Vec<f32>,
    british: bool,
    speed: f32,
}

impl Kokoro {
    pub fn load(voice: &str, speed: f32) -> Result<Self> {
        let dir = Config::models_dir();
        if Command::new("espeak-ng").arg("--version").output().is_err() {
            bail!("espeak-ng is not installed (sudo pacman -S espeak-ng)");
        }
        let config: serde_json::Value = serde_json::from_str(&std::fs::read_to_string(dir.join("kokoro-config.json"))?)?;
        let vocab = config["vocab"]
            .as_object()
            .ok_or_else(|| anyhow!("kokoro config has no vocab"))?
            .iter()
            .filter_map(|(k, v)| Some((k.chars().next()?, v.as_i64()?)))
            .collect();
        let style = load_voice(&dir.join("voices-v1.0.bin"), voice)?;
        let session = crate::onnx::session(&dir.join("kokoro-v1.0.onnx"), 4)?;
        Ok(Self { session, vocab, style, british: voice.starts_with('b'), speed })
    }

    pub fn synthesize(&mut self, text: &str) -> Result<Vec<f32>> {
        let phonemes = phonemize(text, self.british)?;
        let ids: Vec<i64> = phonemes.chars().filter_map(|c| self.vocab.get(&c).copied()).collect();
        let mut audio = Vec::new();
        for chunk in ids.chunks(500) {
            let mut tokens = vec![0i64];
            tokens.extend_from_slice(chunk);
            tokens.push(0);
            let row = chunk.len().min(509);
            let style = self.style[row * 256..(row + 1) * 256].to_vec();
            let n = tokens.len();
            let outputs = self
                .session
                .run(ort::inputs![
                    "tokens" => Tensor::from_array(([1usize, n], tokens))?,
                    "style" => Tensor::from_array(([1usize, 256], style))?,
                    "speed" => Tensor::from_array(([1usize], vec![self.speed]))?,
                ])
                .map_err(|e| anyhow!("kokoro: {e}"))?;
            let (_, samples) = outputs["audio"].try_extract_tensor::<f32>()?;
            audio.extend_from_slice(samples);
        }
        Ok(audio)
    }
}

fn load_voice(archive: &std::path::Path, voice: &str) -> Result<Vec<f32>> {
    let file = std::fs::File::open(archive).with_context(|| format!("opening {}", archive.display()))?;
    let mut zip = zip::ZipArchive::new(file)?;
    let mut entry = zip.by_name(&format!("{voice}.npy")).map_err(|_| anyhow!("unknown voice {voice}"))?;
    let mut bytes = Vec::new();
    entry.read_to_end(&mut bytes)?;
    if &bytes[..6] != b"\x93NUMPY" {
        bail!("voice {voice} is not an .npy array");
    }
    let (header_len, start) = if bytes[6] == 1 {
        (u16::from_le_bytes([bytes[8], bytes[9]]) as usize, 10)
    } else {
        (u32::from_le_bytes([bytes[8], bytes[9], bytes[10], bytes[11]]) as usize, 12)
    };
    let data = &bytes[start + header_len..];
    let floats: Vec<f32> = data.chunks_exact(4).map(|c| f32::from_le_bytes([c[0], c[1], c[2], c[3]])).collect();
    if floats.len() != 510 * 256 {
        bail!("voice {voice} has unexpected size {}", floats.len());
    }
    Ok(floats)
}

const PUNCT: &[char] = &[',', '.', ';', ':', '!', '?', '—', '…'];

fn phonemize(text: &str, british: bool) -> Result<String> {
    let mut out = String::new();
    let mut piece = String::new();
    let flush = |piece: &mut String, punct: Option<char>, out: &mut String| -> Result<()> {
        let words = piece.trim();
        if !words.is_empty() {
            let ipa = espeak(words, british)?;
            if !out.is_empty() && !out.ends_with(' ') {
                out.push(' ');
            }
            out.push_str(ipa.trim());
        }
        if let Some(p) = punct {
            out.push(p);
            out.push(' ');
        }
        piece.clear();
        Ok(())
    };
    for c in text.chars() {
        if PUNCT.contains(&c) {
            flush(&mut piece, Some(c), &mut out)?;
        } else {
            piece.push(c);
        }
    }
    flush(&mut piece, None, &mut out)?;
    Ok(normalize_phonemes(out.trim()))
}

fn espeak(text: &str, british: bool) -> Result<String> {
    let out = Command::new("espeak-ng")
        .args(["-q", "--ipa", "-v", if british { "en-gb" } else { "en-us" }])
        .arg(text)
        .output()
        .context("running espeak-ng")?;
    Ok(String::from_utf8_lossy(&out.stdout).split_whitespace().collect::<Vec<_>>().join(" "))
}

fn normalize_phonemes(p: &str) -> String {
    let mut s = p.replace('ʲ', "j").replace('r', "ɹ").replace('x', "k").replace('ɬ', "l");
    s = Regex::new(r"(?P<a>[a-zɹː])(?P<b>hˈʌndɹɪd)").unwrap().replace_all(&s, "$a $b").to_string();
    s = Regex::new(r" z(?P<e>[;:,.!?¡¿—…]|$)").unwrap().replace_all(&s, "z$e").to_string();
    s = Regex::new(r"nˈaɪnti(?P<n>[^ː]|$)").unwrap().replace_all(&s, "nˈaɪndi$n").to_string();
    s
}

const LEXICON: &[(&str, &str)] = &[
    ("idempotency", "eye-dem-potency"),
    ("idempotent", "eye-dem-potent"),
    ("deque", "deck"),
    ("heapq", "heap Q"),
    ("enum", "ee-num"),
    ("regex", "rej-ex"),
    ("kwargs", "keyword args"),
    ("async", "ay-sync"),
    ("tuple", "tuhple"),
    ("JSON", "jay-son"),
    ("YAML", "yammel"),
    ("UUID", "U U I D"),
    ("OAuth", "oh-auth"),
    ("stdin", "standard in"),
    ("stdout", "standard out"),
    ("nginx", "engine X"),
    ("SaaS", "sass"),
    ("pytest", "pie-test"),
    ("unittest", "unit test"),
    ("bisect", "bye-sect"),
];

fn apply_lexicon(text: &str) -> String {
    let mut s = text.to_string();
    for (word, say) in LEXICON {
        let re = Regex::new(&format!(r"(?i)\b{}\b", regex::escape(word))).unwrap();
        s = re.replace_all(&s, *say).to_string();
    }
    s
}

/// Make interviewer text sound natural when spoken.
pub fn speakable(text: &str) -> String {
    let mut s = text.replace(['*', '`', '#'], "");
    let big_o = Regex::new(r"\bO\(([^)]*)\)").unwrap();
    s = big_o.replace_all(&s, "O of $1").to_string();
    s = s.replace("->", " to ").replace("e.g.", "for example").replace("i.e.", "that is").replace(" vs ", " versus ");
    let file = Regex::new(r"\b([A-Za-z_][A-Za-z0-9_]*)\.(py|md|toml|json)\b").unwrap();
    s = file.replace_all(&s, "$1 dot $2").to_string();
    let snake = Regex::new(r"\b([a-z0-9]+)_([a-z0-9_]+)\b").unwrap();
    while snake.is_match(&s) {
        s = snake.replace_all(&s, "$1 $2").to_string();
    }
    s = s.replace("__", " ").replace('_', " ");
    apply_lexicon(&s).split_whitespace().collect::<Vec<_>>().join(" ")
}

/// Splits streamed text into speakable sentences and drops private tags (<notes>, <control>).
#[derive(Default)]
pub struct SentenceSplitter {
    buf: String,
    hidden: bool,
}

impl SentenceSplitter {
    pub fn push(&mut self, delta: &str) -> Vec<String> {
        if self.hidden {
            return Vec::new();
        }
        self.buf.push_str(delta);
        if let Some(i) = self.buf.find('<') {
            let rest = &self.buf[i..];
            if rest.starts_with("<notes") || rest.starts_with("<control") || (rest.len() < 9 && ("<notes".starts_with(rest) || "<control".starts_with(rest))) {
                if rest.len() >= 6 && (rest.starts_with("<notes") || rest.starts_with("<control")) {
                    self.hidden = true;
                    let before = self.buf[..i].to_string();
                    self.buf.clear();
                    return split_all(&before);
                }
                let before = self.buf[..i].to_string();
                let tail = self.buf[i..].to_string();
                let out = self.take_complete(&before);
                self.buf.push_str(&tail);
                return out;
            }
        }
        let current = std::mem::take(&mut self.buf);
        self.take_complete(&current)
    }

    fn take_complete(&mut self, text: &str) -> Vec<String> {
        let mut out = Vec::new();
        let mut start = 0;
        let chars: Vec<(usize, char)> = text.char_indices().collect();
        for (k, &(i, c)) in chars.iter().enumerate() {
            let next = chars.get(k + 1).map(|x| x.1);
            let boundary = matches!(c, '.' | '!' | '?') && next.is_some_and(|n| n.is_whitespace()) || c == '\n';
            if boundary {
                let end = i + c.len_utf8();
                let sentence = text[start..end].trim();
                if sentence.len() >= 2 {
                    out.push(sentence.to_string());
                }
                start = end;
            }
        }
        self.buf = text[start..].to_string();
        out
    }

    pub fn finish(&mut self) -> Vec<String> {
        let rest = std::mem::take(&mut self.buf);
        self.hidden = false;
        split_all(&rest)
    }
}

fn split_all(text: &str) -> Vec<String> {
    let mut s = SentenceSplitter::default();
    let mut out = s.take_complete(text);
    let tail = s.buf.trim().to_string();
    if !tail.is_empty() && !tail.starts_with('<') {
        out.push(tail);
    }
    out
}

/// Strip private tags from a full reply; returns (spoken text, notes, control json).
pub fn split_reply(reply: &str) -> (String, String, Option<serde_json::Value>) {
    let notes_re = Regex::new(r"(?s)<notes>(.*?)(</notes>|$)").unwrap();
    let control_re = Regex::new(r"(?s)<control>(.*?)(</control>|$)").unwrap();
    let notes = notes_re.captures(reply).map(|c| c[1].trim().to_string()).unwrap_or_default();
    let control = control_re.captures(reply).and_then(|c| serde_json::from_str(c[1].trim()).ok());
    let spoken = control_re.replace_all(&notes_re.replace_all(reply, ""), "").trim().to_string();
    (spoken, notes, control)
}

pub enum TtsCmd {
    Say(String),
}

/// Runs Kokoro on its own thread and plays the audio.
pub fn spawn(voice: String, speed: f32, shared: Arc<Shared>) -> Result<Sender<TtsCmd>> {
    let (tx, rx) = channel::<TtsCmd>();
    let (ready_tx, ready_rx) = channel::<Result<()>>();
    std::thread::spawn(move || {
        let mut engine = match Kokoro::load(&voice, speed) {
            Ok(e) => {
                let _ = ready_tx.send(Ok(()));
                e
            }
            Err(e) => {
                let _ = ready_tx.send(Err(e));
                return;
            }
        };
        while let Ok(TtsCmd::Say(text)) = rx.recv() {
            let text = speakable(&text);
            if text.is_empty() {
                continue;
            }
            match engine.synthesize(&text) {
                Ok(samples) => shared.play(&samples),
                Err(e) => tracing::error!("tts failed: {e:#}"),
            }
        }
    });
    ready_rx.recv().map_err(|_| anyhow!("tts thread died"))??;
    Ok(tx)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn splitter_streams_sentences_and_hides_notes() {
        let mut s = SentenceSplitter::default();
        let mut got = Vec::new();
        for d in ["Hi Fola, I'm Dan", "iel. How are", " you today? <no", "tes>private</notes>", "<control>{}</control>"] {
            got.extend(s.push(d));
        }
        got.extend(s.finish());
        assert_eq!(got, vec!["Hi Fola, I'm Daniel.", "How are you today?"]);
    }

    #[test]
    fn reply_parts() {
        let (spoken, notes, control) = split_reply("Great. <notes>found B1</notes>\n<control>{\"look\": true}</control>");
        assert_eq!(spoken, "Great.");
        assert_eq!(notes, "found B1");
        assert_eq!(control.unwrap()["look"], true);
    }

    #[test]
    fn speakable_text() {
        assert_eq!(speakable("Is `_volume_before` O(n log n)?"), "Is volume before O of n log n?");
        assert_eq!(speakable("open meetings.py"), "open meetings dot py");
    }
}
