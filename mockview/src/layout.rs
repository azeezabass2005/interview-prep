use std::process::Command;
use std::time::Duration;

/// Bring Zed to the front next to the mockview terminal (Hyprland tiles them side by side).
pub fn arrange(mode: &str) {
    if mode == "none" || Command::new("hyprctl").arg("version").output().is_err() {
        return;
    }
    std::thread::spawn(|| {
        for _ in 0..20 {
            std::thread::sleep(Duration::from_millis(500));
            let out = Command::new("hyprctl").args(["clients", "-j"]).output();
            let Ok(out) = out else { return };
            let Ok(clients) = serde_json::from_slice::<serde_json::Value>(&out.stdout) else { return };
            let zed = clients.as_array().into_iter().flatten().find(|c| {
                c["class"].as_str().is_some_and(|k| k.to_lowercase().contains("zed"))
            });
            if let Some(z) = zed {
                if let Some(addr) = z["address"].as_str() {
                    let _ = Command::new("hyprctl").args(["dispatch", "focuswindow", &format!("address:{addr}")]).output();
                }
                return;
            }
        }
    });
}
