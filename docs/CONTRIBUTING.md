# Guide de contribution — Gideonne_1

Merci de vouloir contribuer à Gideonne ! Ce guide explique comment participer.

## Prérequis

- Rust 1.75+ (`rustup update stable`)
- Node.js 20+ et npm 10+
- Tauri CLI v2 (`npm install -g @tauri-apps/cli`)
- Git configuré avec ton nom et email

## Démarrage rapide

```bash
git clone https://github.com/NATH-hub-creator/Gideonne_1.git
cd Gideonne_1
npm install
npm run tauri dev
```

## Conventions

### Rust
- `cargo fmt` avant chaque commit
- `cargo clippy -- -D warnings` sans avertissements
- Commentaires en français, en-tête de module obligatoire
- Erreurs : `anyhow::Result` pour les fonctions publiques

### TypeScript / React
- Composants : un fichier par composant, PascalCase
- Hooks : préfixe `use`, camelCase
- Imports : alias `@/` (ex: `@/components/ChatWindow`)

## Workflow Git

1. Branche depuis `main` : `git checkout -b feat/ma-fonctionnalite`
2. Format commit : `type: description courte`
   - `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
3. Pull Request vers `main`

## Tests

```bash
cargo test --workspace
npm test
```

## Modules en stub (ne pas implémenter sans discussion)

- Vision (YOLO, OpenCV) — prévu v0.3.0
- Voix (Whisper, Piper) — prévu v0.2.0
- Communication (email, WhatsApp) — prévu v0.4.0
