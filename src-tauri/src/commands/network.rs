// commands/network.rs — Scan Wi-Fi et informations réseau
use serde::{Deserialize, Serialize};
use tauri::command;

#[derive(Debug, Serialize, Deserialize)]
pub struct ReseauWifi { pub ssid: String, pub signal: i32, pub securite: String, pub connecte: bool }

#[derive(Debug, Serialize, Deserialize)]
pub struct InfoReseau { pub interface: String, pub adresse_ip: Option<String>, pub adresse_mac: Option<String>, pub connecte: bool }

/// Scanne les réseaux Wi-Fi (Linux via nmcli)
#[command]
pub async fn scanner_wifi() -> Vec<ReseauWifi> {
    #[cfg(target_os = "linux")] {
        use std::process::Command;
        if let Ok(output) = Command::new("nmcli").args(["-t", "-f", "SSID,SIGNAL,SECURITY,ACTIVE", "device", "wifi", "list"]).output() {
            let sortie = String::from_utf8_lossy(&output.stdout);
            return sortie.lines().filter(|l| !l.is_empty()).map(|ligne| {
                let c: Vec<&str> = ligne.splitn(4, ':').collect();
                ReseauWifi {
                    ssid: c.first().unwrap_or(&"").to_string(),
                    signal: c.get(1).and_then(|s| s.parse().ok()).unwrap_or(-100),
                    securite: c.get(2).unwrap_or(&"Inconnu").to_string(),
                    connecte: c.get(3).unwrap_or(&"non") == &"oui",
                }
            }).collect();
        }
    }
    vec![]
}

/// Retourne les informations sur les interfaces réseau actives
#[command]
pub async fn obtenir_infos_reseau() -> Vec<InfoReseau> {
    #[cfg(target_os = "linux")] {
        use std::process::Command;
        if let Ok(output) = Command::new("ip").args(["addr", "show"]).output() {
            let sortie = String::from_utf8_lossy(&output.stdout);
            let mut interfaces = Vec::new();
            let mut iface_courante: Option<String> = None;
            for ligne in sortie.lines() {
                if ligne.starts_with(|c: char| c.is_ascii_digit()) {
                    if let Some(nom) = ligne.split(':').nth(1) { iface_courante = Some(nom.trim().to_string()); }
                } else if ligne.trim().starts_with("inet ") && !ligne.contains("127.0.0.1") {
                    let parties: Vec<&str> = ligne.trim().split_whitespace().collect();
                    let ip = parties.get(1).map(|s| s.split('/').next().unwrap_or("").to_string());
                    if let Some(ref iface) = iface_courante {
                        interfaces.push(InfoReseau { interface: iface.clone(), adresse_ip: ip, adresse_mac: None, connecte: true });
                    }
                }
            }
            return interfaces;
        }
    }
    vec![]
}
