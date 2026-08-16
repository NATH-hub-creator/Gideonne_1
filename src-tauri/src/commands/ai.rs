// commands/ai.rs — Inférence LLM via Ollama
use serde::{Deserialize, Serialize};
use tauri::command;
use anyhow::Result;

#[derive(Debug, Serialize, Deserialize)]
pub struct RequeteIA {
    pub message: String,
    pub modele: String,
    pub historique: Vec<MessageHistorique>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct MessageHistorique {
    pub role: String,
    pub contenu: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct RepOllama { model: String, message: OllamaMessage, done: bool }

#[derive(Debug, Serialize, Deserialize)]
struct OllamaMessage { role: String, content: String }

#[derive(Debug, Serialize, Deserialize)]
pub struct ReponseIA {
    pub contenu: String,
    pub modele: String,
    pub succes: bool,
    pub erreur: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct RepListeModeles { models: Vec<ModeleOllama> }

#[derive(Debug, Serialize, Deserialize)]
struct ModeleOllama { name: String, size: u64 }

/// Envoie un message au LLM via Ollama et retourne la réponse
#[command]
pub async fn envoyer_message(requete: RequeteIA) -> ReponseIA {
    tracing::info!("Envoi message à Ollama — modèle: {}, longueur: {}", requete.modele, requete.message.len());
    match appel_ollama(requete).await {
        Ok(contenu) => ReponseIA { contenu, modele: "ollama".to_string(), succes: true, erreur: None },
        Err(e) => { tracing::error!("Erreur Ollama : {}", e); ReponseIA { contenu: String::new(), modele: String::new(), succes: false, erreur: Some(format!("Erreur Ollama : {}", e)) } }
    }
}

async fn appel_ollama(requete: RequeteIA) -> Result<String> {
    let client = reqwest::Client::new();
    let mut messages: Vec<serde_json::Value> = requete.historique.iter()
        .map(|m| serde_json::json!({"role": m.role, "content": m.contenu})).collect();
    messages.push(serde_json::json!({"role": "user", "content": requete.message}));
    let corps = serde_json::json!({"model": requete.modele, "messages": messages, "stream": false});
    let rep = client.post("http://localhost:11434/api/chat").json(&corps).send().await?;
    let rep_json: RepOllama = rep.json().await?;
    Ok(rep_json.message.content)
}

/// Liste les modèles Ollama disponibles
#[command]
pub async fn lister_modeles() -> Vec<String> {
    match reqwest::Client::new().get("http://localhost:11434/api/tags").send().await {
        Ok(rep) => match rep.json::<RepListeModeles>().await {
            Ok(liste) => liste.models.into_iter().map(|m| m.name).collect(),
            Err(_) => vec![],
        },
        Err(_) => vec![],
    }
}

/// Vérifie si Ollama est disponible et répond
#[command]
pub async fn verifier_ollama() -> bool {
    reqwest::Client::new().get("http://localhost:11434/").send().await
        .map(|r| r.status().is_success()).unwrap_or(false)
}
