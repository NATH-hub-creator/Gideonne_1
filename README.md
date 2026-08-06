# Gideonne_1

Gideonne est une IA conversationnelle modulaire, construite en Python. Ce depot contient la version 1 du projet : une base de code propre, extensible et prete pour l'evolution vers des capacites avancees (memoire, outils externes, multi-agents).

## Structure du projet

```
Gideonne_1/
├── gideonne/                # Package principal
│   ├── __init__.py
│   ├── core/                # Moteur de l'IA
│   │   ├── __init__.py
│   │   ├── agent.py         # Agent principal Gideonne
│   │   ├── memory.py        # Gestion de la memoire conversationnelle
│   │   └── prompt.py        # Construction des prompts systeme
│   ├── models/              # Abstraction des modeles LLM
│   │   ├── __init__.py
│   │   ├── base.py          # Interface abstraite
│   │   └── openai_model.py  # Implementation OpenAI / compatible
│   ├── tools/               # Outils utilisables par l'agent
│   │   ├── __init__.py
│   │   ├── registry.py      # Registre des outils
│   │   └── base_tool.py     # Classe de base pour un outil
│   └── utils/               # Utilitaires transversaux
│       ├── __init__.py
│       ├── config.py        # Chargement de la configuration
│       └── logger.py        # Logging structure
├── tests/                   # Tests unitaires et d'integration
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_memory.py
│   └── test_tools.py
├── scripts/
│   └── run.py               # Point d'entree CLI
├── .env.example             # Variables d'environnement requises
├── .gitignore
├── pyproject.toml           # Configuration du projet (PEP 517/518)
├── requirements.txt
└── README.md
```

## Installation

```bash
# Cloner le depot
git clone https://github.com/NATH-hub-creator/Gideonne_1.git
cd Gideonne_1

# Creer un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Installer les dependances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Editer .env et renseigner vos cles API
```

## Lancement

```bash
python scripts/run.py
```

## Configuration

Toutes les options sont definies dans `.env` (voir `.env.example`). Les cles importantes :

| Variable | Description | Valeur par defaut |
|---|---|---|
| `OPENAI_API_KEY` | Cle API OpenAI ou compatible | obligatoire |
| `OPENAI_BASE_URL` | URL de base du LLM | `https://api.openai.com/v1` |
| `GIDEONNE_MODEL` | Modele LLM a utiliser | `gpt-4o-mini` |
| `GIDEONNE_MAX_TOKENS` | Tokens max par reponse | `2048` |
| `GIDEONNE_MEMORY_SIZE` | Nombre de tours en memoire | `20` |
| `LOG_LEVEL` | Niveau de logging | `INFO` |

## Architecture

Gideonne suit une architecture en couches :

1. **Agent** (`core/agent.py`) : orchestre le cycle perception -> raisonnement -> action.
2. **Memory** (`core/memory.py`) : maintient le contexte conversationnel avec une fenetre glissante.
3. **Model** (`models/`) : abstraction du LLM, facilement remplacable (OpenAI, Anthropic, local).
4. **Tools** (`tools/`) : outils enregistres dynamiquement, appeles par l'agent selon le besoin.

## Tests

```bash
pip install pytest
pytest tests/ -v
```

## Roadmap

- [x] Architecture de base agent / memoire / modele
- [x] Registre d'outils extensible
- [ ] Integration d'outils concrets (recherche web, calendrier, fichiers)
- [ ] Support multi-modeles (Anthropic Claude, Mistral, modele local)
- [ ] Interface web (FastAPI + React)
- [ ] Memoire persistante (base vectorielle)
- [ ] Mode multi-agents

## Licence

MIT — voir `LICENSE` pour le detail.
