// commands/communication.rs — Email + WhatsApp — STUB v0.4.0
use serde::{Deserialize, Serialize};
use tauri::command;

#[derive(Debug, Serialize, Deserialize)]
pub struct ParamsEmail { pub destinataire: String, pub sujet: String, pub corps: String, pub html: bool }

#[derive(Debug, Serialize, Deserialize)]
pub struct ResultatCommunication { pub succes: bool, pub message: String, pub id_message: Option<String> }

/// Envoie un email via SMTP — STUB v0.4.0
#[command]
pub async fn envoyer_email(params: ParamsEmail) -> ResultatCommunication {
    ResultatCommunication {
        succes: false,
        message: format!("Module email non implémenté (prévu v0.4.0). Destinataire : {}", params.destinataire),
        id_message: None,
    }
}
