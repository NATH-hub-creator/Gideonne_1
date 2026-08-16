// commands/system.rs — Commandes système (shell, processus)
use serde::{Deserialize, Serialize};
use tauri::command;
use std::process::Command;

#[derive(Debug, Serialize, Deserialize)]
pub struct ResultatCommande { pub sortie: String, pub erreur: String, pub code_retour: i32, pub succes: bool }

#[derive(Debug, Serialize, Deserialize)]
pub struct InfoProcessus { pub pid: u32, pub nom: String }

/// Exécute une commande shell autorisée
#[command]
pub async fn executer_commande(commande: String, args: Vec<String>) -> ResultatCommande {
    tracing::info!("Exécution commande : {} {:?}", commande, args);
    let autorisees = ["ls", "pwd", "echo", "cat", "date", "uname", "df", "du"];
    if !autorisees.contains(&commande.as_str()) {
        return ResultatCommande { sortie: String::new(), erreur: format!("Commande '{}' non autorisée.", commande), code_retour: -1, succes: false };
    }
    match Command::new(&commande).args(&args).output() {
        Ok(o) => ResultatCommande { sortie: String::from_utf8_lossy(&o.stdout).to_string(), erreur: String::from_utf8_lossy(&o.stderr).to_string(), code_retour: o.status.code().unwrap_or(-1), succes: o.status.success() },
        Err(e) => ResultatCommande { sortie: String::new(), erreur: e.to_string(), code_retour: -1, succes: false },
    }
}

/// Liste les processus en cours (Linux seulement)
#[command]
pub async fn lister_processus() -> Vec<InfoProcessus> {
    #[cfg(target_os = "linux")] {
        let mut procs = Vec::new();
        if let Ok(entrees) = std::fs::read_dir("/proc") {
            for e in entrees.flatten() {
                if let Ok(pid) = e.file_name().to_string_lossy().parse::<u32>() {
                    let nom = std::fs::read_to_string(format!("/proc/{}/comm", pid)).unwrap_or_default().trim().to_string();
                    if !nom.is_empty() { procs.push(InfoProcessus { pid, nom }); }
                }
            }
        }
        procs.sort_by_key(|p| p.pid);
        procs
    }
    #[cfg(not(target_os = "linux"))] { vec![] }
}
