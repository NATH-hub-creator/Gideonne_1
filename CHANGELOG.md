# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.
Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

## [0.1.0] - 2026-07-16

### Ajouté
- Scaffold complet du projet Gideonne_1 (58 fichiers)
- Backend Rust avec Tauri v2 : commandes IA, système, filesystem, réseau, vision, voix, communication, sécurité
- Frontend React 18 avec TypeScript strict : ChatWindow, Sidebar, StatusBar, SettingsPanel, VoiceButton
- Système de mémoire SQLite (conversations + messages)
- Système de plugins extensible
- Journalisation avec `tracing`
- Configuration JSON persistante
- Internationalisation 6 langues : français, anglais, espagnol, mooré, gurunsi, latin
- Intégration Ollama pour l'inférence LLM locale
- Stubs propres pour OpenCV/YOLO (vision), Whisper STT + Piper TTS (voix)
- Stubs pour email et WhatsApp (communication)
- Chiffrement AES-256-GCM pour la sécurité
- Architecture modulaire documentée avec diagrammes ASCII
- Tests unitaires et d'intégration
- Documentation complète (README, ARCHITECTURE, CONTRIBUTING, SECURITY, docs modules)

### Technique
- Rust edition 2021, Tauri v2 (fenêtre 1100x720, mode sombre)
- React 18 + TypeScript + Vite + Zustand + i18next
- SQLite via rusqlite, chiffrement AES-256-GCM via crate `aes-gcm`
