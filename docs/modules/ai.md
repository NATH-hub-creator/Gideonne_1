# Module IA — Gideonne_1

## Vue d'ensemble

Le module IA gère l'inférence LLM locale via **Ollama** (port 11434).

## Commandes Tauri exposées

| Commande | Description |
|----------|-------------|
| `envoyer_message` | Envoie un message au LLM et retourne la réponse |
| `lister_modeles` | Liste les modèles Ollama disponibles |
| `verifier_ollama` | Vérifie la disponibilité d'Ollama |

## Modèles supportés

- `llama3` (défaut), `mistral`, `phi3`, `gemma2`, `qwen2`

## Configuration

```json
{
  "modele_ia": "llama3",
  "url_ollama": "http://localhost:11434"
}
```

## Roadmap

- v0.2.0 : Streaming token par token
- v0.3.0 : Support RAG avec base de documents locale
