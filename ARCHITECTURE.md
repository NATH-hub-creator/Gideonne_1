# Architecture Technique — Gideonne_1

## Vue d'ensemble

```
+-------------------------------------------------------------+
|                        GIDEONNE_1                           |
|                                                             |
|  +---------------------------------------------------------+ |
|  |              FRONTEND (React 18 + TypeScript)           | |
|  |                                                         | |
|  |  ChatWindow | Sidebar | StatusBar | Settings | Voice    | |
|  |  Stores (Zustand) --- Hooks --- i18n (6 langues)        | |
|  +-------------------------+-------------------------------+ |
|                            | Tauri IPC (invoke/emit)        |
|  +-------------------------v-------------------------------+ |
|  |              BACKEND (Rust + Tauri v2)                   | |
|  |                                                         | |
|  |  [AI/Ollama]  [Systeme]  [Fichiers]  [Reseau]          | |
|  |  [Vision*]    [Voix*]    [Comms*]    [Securite]        | |
|  |                   (* = stub, impl. prevue)              | |
|  |                                                         | |
|  |  CORE: Memoire (SQLite) | Plugins | Config | Logger     | |
|  +---------------------------------------------------------+ |
|                            |                                |
|  +-------------------------v-------------------------------+ |
|  |                  STOCKAGE LOCAL                          | |
|  |  gideonne.db (SQLite) | config.json | plugins/          | |
|  +---------------------------------------------------------+ |
+-------------------------------------------------------------+
```

## Flux de données — Conversation IA

```
Utilisateur saisit texte
        |
        v
ChatWindow.tsx (React)
        | invoke("envoyer_message")
        v
commands/ai.rs (Rust)
        | HTTP POST localhost:11434/api/chat
        v
Ollama (LLM local)
        | reponse JSON
        v
core/memory.rs -> sauvegarde SQLite
        | emit("ai_response")
        v
ChatWindow.tsx -> affichage
```

## Module Memoire (SQLite)

```sql
CREATE TABLE conversations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    titre         TEXT    NOT NULL,
    cree_le       TEXT    NOT NULL DEFAULT (datetime('now')),
    mis_a_jour_le TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role            TEXT    NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
    contenu         TEXT    NOT NULL,
    cree_le         TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_messages_conv ON messages(conversation_id);
```

## Technologies

| Couche | Technologie | Justification |
|--------|-------------|---------------|
| Desktop | Tauri v2 | Léger, sécurisé, Rust natif |
| Backend | Rust 2021 | Performance, sécurité mémoire |
| Frontend | React 18 + TS | Écosystème riche, typage fort |
| État | Zustand | Simple, performant |
| Build | Vite | Rapide, ESM natif |
| DB locale | SQLite / rusqlite | Embarquable, zéro configuration |
| LLM | Ollama | LLM local, multi-modèles |
| i18n | i18next | Standard de l'industrie |
