// commands/voice.rs — Whisper STT + Piper TTS — STUB v0.2.0
use serde::{Deserialize, Serialize};
use tauri::command;

#[derive(Debug, Serialize, Deserialize)]
pub struct ResultatSTT { pub succes: bool, pub transcription: Option<String>, pub langue_detectee: Option<String>, pub message: String }

#[derive(Debug, Serialize, Deserialize)]
pub struct ResultatTTS { pub succes: bool, pub message: String, pub chemin_audio: Option<String> }

/// Démarre l'écoute microphone — STUB v0.2.0
#[command]
pub async fn demarrer_ecoute(_duree_secondes: u32, _langue: Option<String>) -> ResultatSTT {
    ResultatSTT {
        succes: false,
        transcription: None,
        langue_detectee: None,
        message: "Module voix (STT) non implémenté (prévu v0.2.0). Installer Whisper STT pour activer.".to_string(),
    }
}

/// Synthèse vocale Piper TTS — STUB v0.2.0
#[command]
pub async fn synthese_vocale(texte: String, _voix: Option<String>) -> ResultatTTS {
    ResultatTTS {
        succes: false,
        message: format!("Module TTS non implémenté (prévu v0.2.0). {} caractères reçus.", texte.len()),
        chemin_audio: None,
    }
}
