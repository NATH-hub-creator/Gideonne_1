# Module Plugins — Gideonne_1

## Structure d'un plugin

```
~/.gideonne/plugins/
└── mon-plugin/
    ├── manifest.json
    └── README.md
```

## Format du manifest.json

```json
{
  "id": "mon-plugin-id",
  "nom": "Mon Plugin",
  "version": "1.0.0",
  "description": "Ce plugin fait X et Y.",
  "auteur": "Votre Nom",
  "actif": true
}
```

## Cycle de vie

1. Au démarrage, `core::initialiser()` appelle `charger_plugins()`
2. Chaque sous-dossier de `~/.gideonne/plugins/` est analysé
3. Si `manifest.json` est valide et `actif: true`, le plugin est enregistré

## Roadmap

- v0.2.0 : Interface de gestion des plugins dans SettingsPanel
- v0.5.0 : Plugins Rust natifs avec ABI stable
- v1.0.0 : Marketplace communautaire
