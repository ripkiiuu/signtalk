# SIGNTALK — Project Instructions for OpenCode

## Product
SIGNTALK is an Indonesian-language, accessible Progressive Web App for learning American Sign Language (ASL), developed as a 2026 student PKM-KC prototype. Primary flow: Learn -> Watch -> Practice -> Live Feedback -> Result -> Progress. ASL is an independent language; this app is not a BISINDO translator.

## Read this first
- Inspect the existing repository, current Git status, and app architecture before editing.
- Preserve existing code, UI, assets, package manager and conventions; extend rather than rewrite.
- Do not execute destructive cleanup, reset, migrations, force pushes or paid cloud operations without explicit user approval.
- Document progress and known limitations in `docs/STATUS.md`.

## Core requirements
- PWA must be responsive, installable, accessible and use HTTPS/localhost for camera access.
- Features: ASL Vocabulary Learning; Common ASL Phrases (official YouTube embeds, correct source attribution); AI Sign Recognition; Live Visual Feedback; Mini Challenge; Final Evaluation; Progress Dashboard.
- MediaPipe hand/face/pose landmarks are DETECTION only. Never interpret successful landmark detection as correct ASL. Separate `detection`, `recognition`, and `validated coaching` states.
- Green/red feedback only for components supported by real measured criteria; yellow/neutral for low-confidence or unassessed components. Never fabricate evaluation metrics or model weights.
- Facial-expression assessment must be ASL-contextual and require competent ASL validation; otherwise use detection-only status.
- Real camera frames remain local whenever possible; never collect, upload, log, or persist raw user video without explicit informed consent.
- Video embeds are not training datasets. Respect YouTube terms and dataset license/attribution. Do not bulk download datasets (>1 GB) or scrape videos without user approval.

## Suggested architecture (adapt to actual repository)
- Frontend: existing React/TypeScript or equivalent; Vite/Tailwind if already present.
- Vision: MediaPipe Tasks Vision in browser.
- Training: Python + MediaPipe + a tested baseline and optional temporal GRU/BiLSTM.
- Browser inference: ONNX Runtime Web or TensorFlow.js, selected for proven export/inference compatibility.
- Folders: `ai/`, `datasets/raw/`, `datasets/processed/`, `models/`, `docs/`; avoid reorganizing app if not needed.
- Exclude dataset videos, heavyweight models, `.env` and secrets from Git. Maintain `.env.example` and reproducible scripts.

## Training quality
- Use official ASL dataset sources and their usage terms; never invent classes or metadata.
- Split evaluation by signer when possible; report limitations otherwise.
- Track model input shape, label mapping, preprocessing config, accuracy/F1/confusion matrix, and latency.
- Implement unknown/low-confidence cases; do not force all frames into a known sign class.
- Do not assert that isolated-word classification evaluates phrases or full ASL grammar.

## Verification and communication
- After relevant code edits, run available typecheck/lint/tests/build and document actual results.
- Keep changes incremental and runnable; if data/licenses are unavailable, build an explicit demo mode rather than fake a trained AI.
- At completion provide exact local Windows commands to run the app, perform training, and test camera behavior, plus actual blockers and status.
