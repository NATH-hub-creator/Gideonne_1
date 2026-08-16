// core/mod.rs — Module core de Gideonne
pub mod config;
pub mod logger;
pub mod memory;
pub mod plugins;

use tauri::AppHandle;
use anyhow::Result;
use tracing::info;

/// Initialise tous les composants du core au démarrage
pub async fn initialiser(app: &AppHandle) -> Result<()> {
    info!("Initialisation du core Gideonne...");
    config::initialiser_config(app).await?;
    info!("  Config chargée");
    memory::initialiser_db(app).await?;
    info!("  Base de données initialisée");
    plugins::charger_plugins(app).await?;
    info!("  Plugins chargés");
    info!("Core Gideonne prêt.");
    Ok(())
}
