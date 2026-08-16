// commands/filesystem.rs — CRUD fichiers et dossiers
use serde::{Deserialize, Serialize};
use tauri::command;
use std::{fs, path::Path};

#[derive(Debug, Serialize, Deserialize)]
pub struct ElementFs { pub nom: String, pub chemin: String, pub est_dossier: bool, pub taille: u64 }

#[derive(Debug, Serialize, Deserialize)]
pub struct ResultatFs { pub succes: bool, pub message: String }

/// Lit le contenu d'un fichier texte
#[command]
pub async fn lire_fichier(chemin: String) -> Result<String, String> {
    fs::read_to_string(&chemin).map_err(|e| e.to_string())
}

/// Ecrit du contenu dans un fichier
#[command]
pub async fn ecrire_fichier(chemin: String, contenu: String) -> ResultatFs {
    match fs::write(&chemin, &contenu) {
        Ok(_) => ResultatFs { succes: true, message: format!("Fichier '{}' écrit.", chemin) },
        Err(e) => ResultatFs { succes: false, message: e.to_string() },
    }
}

/// Liste les éléments d'un répertoire
#[command]
pub async fn lister_dossier(chemin: String) -> Vec<ElementFs> {
    let mut elements = Vec::new();
    if let Ok(entrees) = fs::read_dir(Path::new(&chemin)) {
        for e in entrees.flatten() {
            if let Ok(meta) = e.metadata() {
                elements.push(ElementFs {
                    nom: e.file_name().to_string_lossy().to_string(),
                    chemin: e.path().to_string_lossy().to_string(),
                    est_dossier: meta.is_dir(),
                    taille: if meta.is_file() { meta.len() } else { 0 },
                });
            }
        }
    }
    elements.sort_by(|a, b| b.est_dossier.cmp(&a.est_dossier).then(a.nom.to_lowercase().cmp(&b.nom.to_lowercase())));
    elements
}

/// Supprime un fichier ou dossier
#[command]
pub async fn supprimer_element(chemin: String, recursif: bool) -> ResultatFs {
    let path = Path::new(&chemin);
    let r = if path.is_dir() && recursif { fs::remove_dir_all(path) } else if path.is_dir() { fs::remove_dir(path) } else { fs::remove_file(path) };
    match r {
        Ok(_) => ResultatFs { succes: true, message: format!("'{}' supprimé.", chemin) },
        Err(e) => ResultatFs { succes: false, message: e.to_string() },
    }
}
