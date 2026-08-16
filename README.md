# Gideonne_1

> Assistant IA local, modulaire et multilingue — propulsé par Rust, Tauri v2 et React 18.

[![Licence MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)
[![Rust](https://img.shields.io/badge/rust-2021_edition-orange.svg)](https://www.rust-lang.org)
[![Tauri](https://img.shields.io/badge/tauri-v2-purple.svg)](https://tauri.app)
[![React](https://img.shields.io/badge/react-18-61DAFB.svg)](https://reactjs.org)

---

## Présentation

Gideonne_1 est un assistant IA personnel fonctionnant **entièrement en local**, sans dépendance cloud. Il s'appuie sur Ollama pour l'inférence LLM et intègre des capacités de vision (YOLO/OpenCV), reconnaissance et synthèse vocale (Whisper / Piper TTS).

### Caractéristiques clés

- **100 % local** : aucune donnée envoyée vers des serveurs tiers
- **Multilingue** : français, anglais, espagnol, mooré, gurunsi, latin
- **Modulaire** : architecture en plugins, chaque capacité est indépendante
- **Sécurisé** : chiffrement AES-256-GCM, gestion fine des permissions
- **Extensible** : système de plugins Rust

---

## Prérequis

| Outil | Version minimale |
|-------|------------------|
| Rust  | 1.75+            |
| Node.js | 20+            |
| npm   | 10+              |
| Tauri CLI | 2.0+         |
| Ollama | 0.1.30+        |

---

## Installation

```bash
git clone https://github.com/NATH-hub-creator/Gideonne_1.git
cd Gideonne_1
npm install
ollama serve  # Dans un terminal séparé
ollama pull llama3
npm run tauri dev
```

---

## Architecture

```
Gideonne_1/
├── src-tauri/          # Backend Rust (Tauri v2)
│   └── src/
│       ├── commands/   # Commandes exposées au frontend
│       ├── core/       # Mémoire, plugins, config, journaux
│       └── i18n/       # Internationalisation backend
├── src/                # Frontend React + TypeScript
│   ├── components/
│   ├── hooks/
│   ├── stores/
│   └── i18n/           # 6 langues
├── docs/               # Documentation technique
└── tests/              # Tests unitaires et d'intégration
```

## Modules

| Module | Description | Statut |
|--------|-------------|--------|
| AI (Ollama) | Inférence LLM locale | Fonctionnel |
| Mémoire (SQLite) | Persistance conversations | Fonctionnel |
| Système | Commandes shell | Fonctionnel |
| Filesystem | CRUD fichiers/dossiers | Fonctionnel |
| Réseau | Scan Wi-Fi, interfaces | Fonctionnel |
| Vision | YOLO, OCR, caméras | Stub (v0.3.0) |
| Voix | Whisper STT, Piper TTS | Stub (v0.2.0) |
| Communication | Email, WhatsApp | Stub (v0.4.0) |
| Sécurité | AES-256-GCM | Fonctionnel |
| Plugins | Système d'extension | Fonctionnel |
| i18n | 6 langues | Fonctionnel |

## Roadmap

- [ ] v0.2.0 : Intégration réelle Whisper STT
- [ ] v0.3.0 : Vision YOLO avec OpenCV
- [ ] v0.4.0 : Communication email/WhatsApp
- [ ] v1.0.0 : Version stable complète

## Licence

MIT © 2026 Nathanael (NATH-hub-creator)
