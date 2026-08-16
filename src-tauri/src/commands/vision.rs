// commands/vision.rs — Vision (YOLO, OCR, caméras) — STUB v0.3.0
use serde::{Deserialize, Serialize};
use tauri::command;

#[derive(Debug, Serialize, Deserialize)]
pub struct ResultatVision { pub succes: bool, pub message: String, pub objets: Vec<ObjetDetecte>, pub texte_ocr: Option<String> }

#[derive(Debug, Serialize, Deserialize)]
pub struct ObjetDetecte { pub label: String, pub confiance: f32 }

#[derive(Debug, Serialize, Deserialize)]
pub struct ResultatCamera { pub succes: bool, pub message: String, pub cameras_disponibles: Vec<String> }

/// Démarre la capture depuis une caméra — STUB v0.3.0
#[command]
pub async fn demarrer_camera(_index_camera: u32) -> ResultatCamera {
    ResultatCamera {
        succes: false,
        message: "Module vision non implémenté (prévu v0.3.0). Installer OpenCV + YOLO pour activer.".to_string(),
        cameras_disponibles: vec![],
    }
}

/// Analyse une image (YOLO + OCR) — STUB v0.3.0
#[command]
pub async fn analyser_image(chemin_image: String) -> ResultatVision {
    ResultatVision {
        succes: false,
        message: format!("Module vision non implémenté (prévu v0.3.0). Image : {}", chemin_image),
        objets: vec![],
        texte_ocr: None,
    }
}
