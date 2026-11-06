use std::path::{Path, PathBuf};

use anyhow::{Context, Result};
use serde::Deserialize;

#[derive(Debug, Clone, Deserialize)]
#[serde(default)]
pub struct Config {
    pub interview: InterviewCfg,
    pub audio: AudioCfg,
    pub stt: SttCfg,
    pub tts: TtsCfg,
    pub claude: ClaudeCfg,
    pub layout: LayoutCfg,
    pub editor: EditorCfg,
    pub paths: PathsCfg,
    #[serde(skip)]
    pub root: PathBuf,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default)]
pub struct InterviewCfg {
    pub minutes: u32,
    pub exercise_pool: Vec<String>,
    pub check_in_minutes: u32,
    pub silence_prompt_seconds: u32,
    pub no_test_change_minutes: u32,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default)]
pub struct AudioCfg {
    pub input: String,
    pub output: String,
    pub endpoint_silence_ms: u32,
    pub record_audio: bool,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default)]
pub struct SttCfg {
    pub model: String,
    pub threads: i32,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default)]
pub struct TtsCfg {
    pub speed: f32,
    pub voice: String,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default)]
pub struct ClaudeCfg {
    pub model: String,
    pub screenshot_width: u32,
    pub screenshots: bool,
}

#[derive(Debug, Clone, Default, Deserialize)]
#[serde(default)]
pub struct PathsCfg {
    pub kit: String,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default)]
pub struct EditorCfg {
    pub command: String,
    pub open_debrief: bool,
}

impl Default for EditorCfg {
    fn default() -> Self {
        Self { command: "zeditor".into(), open_debrief: true }
    }
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default)]
pub struct LayoutCfg {
    pub mode: String,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            interview: InterviewCfg::default(),
            audio: AudioCfg::default(),
            stt: SttCfg::default(),
            tts: TtsCfg::default(),
            claude: ClaudeCfg::default(),
            layout: LayoutCfg::default(),
            editor: EditorCfg::default(),
            paths: PathsCfg::default(),
            root: PathBuf::from("."),
        }
    }
}

impl Default for InterviewCfg {
    fn default() -> Self {
        Self {
            minutes: 60,
            exercise_pool: vec!["round-1".into()],
            check_in_minutes: 8,
            silence_prompt_seconds: 90,
            no_test_change_minutes: 6,
        }
    }
}

impl Default for AudioCfg {
    fn default() -> Self {
        Self { input: "default".into(), output: "default".into(), endpoint_silence_ms: 1300, record_audio: false }
    }
}

impl Default for SttCfg {
    fn default() -> Self {
        Self { model: "auto".into(), threads: 8 }
    }
}

impl Default for TtsCfg {
    fn default() -> Self {
        Self { speed: 1.0, voice: "auto".into() }
    }
}

impl Default for ClaudeCfg {
    fn default() -> Self {
        Self { model: String::new(), screenshot_width: 1600, screenshots: true }
    }
}

impl Default for LayoutCfg {
    fn default() -> Self {
        Self { mode: "side".into() }
    }
}

impl Config {
    pub fn load(explicit: Option<&Path>) -> Result<Self> {
        let explicit = explicit.map(|p| std::path::absolute(p).unwrap_or_else(|_| p.to_path_buf()));
        let explicit = explicit.as_deref();
        let root = match explicit {
            Some(p) => p.parent().map(Path::to_path_buf).unwrap_or_else(|| PathBuf::from(".")),
            None => find_root()?,
        };
        let path = explicit.map(Path::to_path_buf).unwrap_or_else(|| root.join("mockview.toml"));
        let mut cfg: Config = if path.exists() {
            toml::from_str(&std::fs::read_to_string(&path)?).with_context(|| format!("reading {}", path.display()))?
        } else {
            Config::default()
        };
        cfg.root = root.canonicalize().unwrap_or(root);
        Ok(cfg)
    }

    pub fn kit(&self) -> PathBuf {
        if !self.paths.kit.is_empty() {
            let expanded = self.paths.kit.replacen('~', &dirs::home_dir().unwrap_or_default().to_string_lossy(), 1);
            return PathBuf::from(expanded);
        }
        self.root.parent().map(Path::to_path_buf).unwrap_or_else(|| self.root.clone())
    }

    pub fn runs_dir(&self) -> PathBuf {
        self.root.join("runs")
    }

    pub fn prompts_dir(&self) -> PathBuf {
        self.root.join("prompts")
    }

    pub fn resume_dir(&self) -> PathBuf {
        self.root.join("resume")
    }

    pub fn models_dir() -> PathBuf {
        dirs::data_dir().unwrap_or_else(|| PathBuf::from(".")).join("mockview/models")
    }
}

fn find_root() -> Result<PathBuf> {
    if let Ok(home) = std::env::var("MOCKVIEW_HOME") {
        return Ok(PathBuf::from(home));
    }
    let mut dir = std::env::current_dir()?;
    loop {
        if dir.join("mockview.toml").exists() {
            return Ok(dir);
        }
        if dir.join("mockview/mockview.toml").exists() {
            return Ok(dir.join("mockview"));
        }
        if !dir.pop() {
            break;
        }
    }
    if let Ok(exe) = std::env::current_exe() {
        for anc in exe.ancestors() {
            if anc.join("mockview.toml").exists() {
                return Ok(anc.to_path_buf());
            }
        }
    }
    let fallback = dirs::home_dir().unwrap_or_default().join("Projects/interview-prep/mockview");
    Ok(fallback)
}
