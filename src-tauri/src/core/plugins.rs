// core/plugins.rs — Système de plugins extensibles
use serde::{Deserialize, Serialize};
use tauri::AppHandle;
use anyhow::Result;
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct MetadataPlugin { pub id: String, pub nom: String, pub version: String, pub description: String, pub auteur: String, pub actif: bool }

static PLUGINS: std::sync::OnceLock<std::sync::Mutex<HashMap<String, MetadataPlugin>>> = std::sync::OnceLock::new();

/// Charge les plugins depuis ~/.gideonne/plugins/
pub async fn charger_plugins(app: &AppHandle) -> Result<()> {
    let reg = PLUGINS.get_or_init(|| std::sync::Mutex::new(HashMap::new()));
    let mut p = app.path().app_data_dir().map_err(|e| anyhow::anyhow!("Err: {}", e))?;
    p.push("plugins");
    if !p.exists() { std::fs::create_dir_all(&p)?; return Ok(()); }
    let mut nb = 0;
    if let Ok(entrees) = std::fs::read_dir(&p) {
        for e in entrees.flatten() {
            if e.path().is_dir() {
                let manifest = e.path().join("manifest.json");
                if manifest.exists() {
                    if let Ok(c) = std::fs::read_to_string(&manifest) {
                        if let Ok(meta) = serde_json::from_str::<MetadataPlugin>(&c) {
                            if let Ok(mut r) = reg.lock() { r.insert(meta.id.clone(), meta); }
                            nb += 1;
                        }
                    }
                }
            }
        }
    }
    tracing::info!("{} plugin(s) chargé(s).", nb);
    Ok(())
}

pub fn lister_plugins() -> Vec<MetadataPlugin> {
    if let Some(r) = PLUGINS.get() { if let Ok(r) = r.lock() { return r.values().cloned().collect(); } }
    vec![]
}
