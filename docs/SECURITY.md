# Politique de sécurité — Gideonne_1

## Modèle de sécurité

Gideonne fonctionne **entièrement en local**. Aucune donnée n'est envoyée vers des serveurs tiers.

## Données stockées

| Type | Emplacement | Chiffrement |
|------|-------------|-------------|
| Conversations | `~/.gideonne/gideonne.db` (SQLite) | Non (local uniquement) |
| Configuration | `~/.gideonne/config.json` | Non |
| Clés API tierces | `~/.gideonne/secrets.enc` | Oui (AES-256-GCM) |
| Journaux | `~/.gideonne/logs/` | Non |

## Signaler une vulnérabilité

1. Ne pas ouvrir une issue publique GitHub
2. Email : yiyenathanael@gmail.com
3. Inclure : description, étapes de reproduction, impact
4. Délai de réponse : 72 heures

## Dépendances de sécurité

| Crate | Usage | Version |
|-------|-------|---------|
| `aes-gcm` | Chiffrement AES-256-GCM | 0.10 |
| `rand` | Génération de nonces sécurisés | 0.8 |
| `rusqlite` | SQLite avec requêtes paramétrées | 0.31 |
