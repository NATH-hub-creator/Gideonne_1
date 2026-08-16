// core/logger.rs — Journalisation structurée avec tracing
use anyhow::Result;
use std::path::PathBuf;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum NiveauLog { Debug, Info, Avertissement, Erreur }

impl std::fmt::Display for NiveauLog {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self { Self::Debug=>write!(f,"DEBUG"), Self::Info=>write!(f,"INFO"), Self::Avertissement=>write!(f,"WARN"), Self::Erreur=>write!(f,"ERROR") }
    }
}

/// Initialise le système de journalisation
pub fn initialiser_logger(chemin_logs: &PathBuf, niveau: NiveauLog) -> Result<()> {
    std::fs::create_dir_all(chemin_logs)?;
    let filtre = match niveau { NiveauLog::Debug=>"debug", NiveauLog::Info=>"info", NiveauLog::Avertissement=>"warn", NiveauLog::Erreur=>"error" };
    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::new(format!("gideonne={filtre},tauri=warn")))
        .compact().init();
    tracing::info!("Journalisation initialisée — niveau: {}", niveau);
    Ok(())
}

pub fn chemin_log_courant(repertoire: &PathBuf) -> PathBuf {
    repertoire.join(format!("gideonne-{}.log", chrono::Local::now().format("%Y-%m-%d")))
}
