// lib.rs — Bibliothèque principale Gideonne
// Enregistre toutes les commandes Tauri et initialise le core

mod commands;
mod core;
mod i18n;

use tauri::Manager;
use tracing::info;

/// Point d'entrée de la lib — appelé par main.rs
pub fn run() {
    tracing_subscriber::fmt()
        .with_env_filter("gideonne=debug,tauri=warn")
        .init();

    info!("Démarrage de Gideonne v{}", env!("CARGO_PKG_VERSION"));

    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            let app_handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                if let Err(e) = core::initialiser(&app_handle).await {
                    tracing::error!("Erreur d'initialisation du core : {}", e);
                }
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            // Module IA
            commands::ai::envoyer_message,
            commands::ai::lister_modeles,
            commands::ai::verifier_ollama,
            // Module système
            commands::system::executer_commande,
            commands::system::lister_processus,
            // Module fichiers
            commands::filesystem::lire_fichier,
            commands::filesystem::ecrire_fichier,
            commands::filesystem::lister_dossier,
            commands::filesystem::supprimer_element,
            // Module réseau
            commands::network::scanner_wifi,
            commands::network::obtenir_infos_reseau,
            // Module vision (stubs)
            commands::vision::demarrer_camera,
            commands::vision::analyser_image,
            // Module voix (stubs)
            commands::voice::demarrer_ecoute,
            commands::voice::synthese_vocale,
            // Module communication (stubs)
            commands::communication::envoyer_email,
            // Module sécurité
            commands::security::chiffrer_donnees,
            commands::security::dechiffrer_donnees,
            // Mémoire
            core::memory::creer_conversation,
            core::memory::ajouter_message,
            core::memory::lister_conversations,
            core::memory::charger_conversation,
        ])
        .run(tauri::generate_context!())
        .expect("Erreur lors du démarrage de l'application Tauri");
}
