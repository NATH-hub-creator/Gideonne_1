# Module Vision — Gideonne_1

**Statut : STUB — Prévu en v0.3.0**

## Fonctionnalités prévues

- Détection d'objets en temps réel via YOLO v8 (ONNX Runtime)
- OCR multilingue via Tesseract
- Capture depuis la webcam ou une image existante

## Commandes Tauri (stubs)

| Commande | Statut |
|----------|--------|
| `demarrer_camera` | STUB |
| `analyser_image` | STUB |

## Dépendances requises (v0.3.0)

```toml
opencv = { version = "0.92" }
ort = { version = "2.0" }  # ONNX Runtime
leptess = "0.14"  # Tesseract OCR
```
