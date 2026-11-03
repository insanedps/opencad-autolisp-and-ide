use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

fn find_codec_source(lock_content: &str) -> Option<String> {
    let mut in_pkg = false;
    let mut is_codec = false;
    for line in lock_content.lines() {
        let line = line.trim();
        if line == "[[package]]" {
            in_pkg = true;
            is_codec = false;
            continue;
        }
        if in_pkg {
            if line == "name = \"opencadcodec\"" || line == "name = \"acadrust\"" {
                is_codec = true;
            } else if is_codec && line.starts_with("source = \"") {
                let s = line.strip_prefix("source = \"")?.strip_suffix("\"")?;
                return Some(s.to_string());
            }
        }
    }
    None
}

fn update_manifest(manifest_path: &Path, codec_source: &str, rustc_ver: &str) {
    if !manifest_path.exists() {
        return;
    }
    let content = match fs::read_to_string(manifest_path) {
        Ok(c) => c,
        Err(_) => return,
    };

    let mut lines: Vec<String> = Vec::new();
    let mut changed = false;

    for line in content.lines() {
        if line.trim_start().starts_with("acadrust_source =") {
            let new_line = format!("acadrust_source = \"{}\"", codec_source);
            if line.trim() != new_line.trim() {
                lines.push(new_line);
                changed = true;
            } else {
                lines.push(line.to_string());
            }
        } else if line.trim_start().starts_with("rustc_version =") {
            let new_line = format!("rustc_version = \"{}\"", rustc_ver);
            if line.trim() != new_line.trim() {
                lines.push(new_line);
                changed = true;
            } else {
                lines.push(line.to_string());
            }
        } else {
            lines.push(line.to_string());
        }
    }

    if changed {
        let mut new_content = lines.join("\r\n");
        if content.ends_with('\n') {
            new_content.push_str("\r\n");
        }
        let _ = fs::write(manifest_path, new_content);
    }
}

fn main() {
    let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap());
    let lock_path = manifest_dir.join("Cargo.lock");

    println!("cargo:rerun-if-changed={}", lock_path.display());
    println!("cargo:rerun-if-env-changed=RUSTC");

    let rustc = env::var_os("RUSTC").unwrap_or_else(|| "rustc".into());
    let rustc_version = Command::new(rustc)
        .arg("--version")
        .output()
        .ok()
        .and_then(|o| {
            if o.status.success() {
                Some(String::from_utf8_lossy(&o.stdout).trim().to_string())
            } else {
                None
            }
        })
        .unwrap_or_default();

    let lock_content = match fs::read_to_string(&lock_path) {
        Ok(c) => c,
        Err(_) => return,
    };

    let codec_source = match find_codec_source(&lock_content) {
        Some(s) => s,
        None => return,
    };

    // Check against OpenCADStudio host Cargo.lock to notify if out of sync
    let host_candidates = [
        manifest_dir.parent().map(|p| p.join("OpenCADStudio-fork")),
        manifest_dir.parent().map(|p| p.join("OpenCADStudio")),
    ];
    for cand in host_candidates.into_iter().flatten() {
        let host_lock = cand.join("Cargo.lock");
        if host_lock.exists() {
            if let Ok(host_content) = fs::read_to_string(&host_lock) {
                if let Some(host_source) = find_codec_source(&host_content) {
                    if host_source != codec_source {
                        println!(
                            "cargo:warning=opencadcodec mismatch! Runner: {} vs Host: {}. Run 'cargo update -p opencadcodec'",
                            codec_source, host_source
                        );
                    }
                }
            }
            break;
        }
    }

    // 1. Update Cargo.toml manifest_dir/plugin.toml
    let plugin_toml = manifest_dir.join("plugin.toml");
    update_manifest(&plugin_toml, &codec_source, &rustc_version);

    // 2. Also keep target directory plugin.toml updated if target exists
    if let Ok(out_dir) = env::var("OUT_DIR") {
        let out_path = PathBuf::from(out_dir);
        // OUT_DIR is target/<profile>/build/<pkg>/out -> go up 3 levels to target/<profile>
        if let Some(target_dir) = out_path.parent().and_then(|p| p.parent()).and_then(|p| p.parent()) {
            let target_plugin = target_dir.join("plugin.toml");
            let _ = fs::copy(&plugin_toml, &target_plugin);
        }
    }

    // 3. Keep installed plugin manifest in AppData in sync if installed
    if let Ok(appdata) = env::var("APPDATA") {
        let appdata_plugin = PathBuf::from(appdata)
            .join("OpenCADStudio")
            .join("plugins")
            .join("opencad.pyrunner")
            .join("plugin.toml");
        if appdata_plugin.exists() {
            let _ = fs::copy(&plugin_toml, &appdata_plugin);
        }
    }
}
