// core/config.rs — Configuration JSON persistante
use serde::{Deserialize, Serialize};
use tauri::AppHandle;
use anyhow::Result;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ConfigGideonne {
    pub version: u32, pub modele_ia: String, pub langue: String, pub mode_sombre: bool,
    pub url_ollama: String, pub fenetre: ConfigFenetre, pub voix: ConfigVoix,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ConfigFenetre { pub largeur: u32, pub hauteur: u32, pub maximisee: bool }

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ConfigVoix { pub activee: bool, pub voix_tts: String, pub vitesse: f32 }

impl Default for ConfigGideonne {
    fn default() -> Self { Self {
        version: 1, modele_ia: "llama3".to_string(), langue: "fr".to_string(), mode_sombre: true,
        url_ollama: "http://localhost:11434".to_string(),
        fenetre: ConfigFenetre { largeur: 1100, hauteur: 720, maximisee: false },
        voix: ConfigVoix { activee: false, voix_tts: "fr_FR-siwis-medium".to_string(), vitesse: 1.0 },
    }}
}

pub async fn initialiser_config(app: &AppHandle) -> Result<()> {
    let chemin = chemin_config(app)?;
    if chemin.exists() {
        let _: ConfigGideonne = serde_json::from_str(&std::fs::read_to_string(&chemin)?)?;
    } else {
        if let Some(p) = chemin.parent() { std::fs::create_dir_all(p)?; }
        std::fs::write(&chemin, serde_json::to_string_pretty(&ConfigGideonne::default())?)?;
    }
    Ok(())
}

fn chemin_config(app: &AppHandle) -> Result<std::path::PathBuf> {
    let mut p = app.path().app_config_dir().map_err(|e| anyhow::anyhow!("Err: {}", e))?;
    p.push("config.json");
    Ok(p)
}
