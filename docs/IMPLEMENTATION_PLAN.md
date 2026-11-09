# SIGNTALK implementation plan

## Audit snapshot — 8 November 2026

- Existing product: React 19 + TypeScript + Vite 8 + Tailwind v4, R3F/Three.js, React Router, PWA Workbox. Existing app is runnable; preserve it.
- Existing P0: six-beat desktop 3D story + mobile illustration, bilingual starter content (2 vocabulary + 2 phrases), official Lifeprint/ASL University references, MediaPipe 0.10.35 hand tracking and optional face/pose detection from local assets, framing feedback, unscored challenge/result, local progress, PWA shell.
- Repository has no `.git`; `git status` is unavailable. No changes were reset or discarded. The nested instruction package was copied to root as `AGENTS.md` and `MASTER_TASK_OPENCODE_SIGNTALK.md` because those files were requested there; originals remain in `signtalk_opencode_package/`.
- `ai/` and `models/` were empty at audit. `datasets/WLASL/` is present and was preserved. It includes the 12.3 MB WLASL v0.3 JSON manifest, upstream scripts/source and the C-UDA PDF, but no raw or processed video and no model weights.
- WLASL manifest audit: 2,000 glosses, 21,083 instances; `sorry` has 14 metadata instances. Its upstream train/val/test splits share signers (108 train/val, 104 train/test, 98 val/test), so those splits are not suitable for subject-independent claims. C-UDA allows computational use but disclaims upstream rights; no video download/scrape was attempted.
- Official ASL Citizen source: Microsoft lists an 84k-video 2,700-sign corpus and a 42.8 GB archive. Its research license is non-commercial/non-revenue research only, data cannot be redistributed, and use must match participant consent. It was not downloaded.
- Environment: Python 3.12 is default; numpy, pandas, scikit-learn present; Python MediaPipe, OpenCV and PyTorch absent. Python 3.14 launcher also exists but may not support MediaPipe wheels. A user screenshot showed one physical hand tracked; controlled camera/overlay validation is not available to automated tests.

## Priorities and completion gates

### P0 — Maintain a usable learning PWA (existing; continue regression testing)
- Keep current visual identity and all routes.
- Preserve camera local processing, detection/recognition/evaluation separation, content provenance/review tags, local progress and deletion.
- Gate: production build, browser smoke (WebGL/fallback, learning sources, responsive layout, permissions, camera tracking adapter, result/progress) and offline app shell pass.

### P1 — Reproducible data-to-baseline tooling (this work)
- Inspect only the local WLASL metadata; report classes, counts, signer IDs/splits, available local video count, and C-UDA caveat.
- Build an explicit 8-class starter metadata subset only from labels that actually exist; split by signer ID (not the upstream split); never fetch videos.
- Current labels: `who`, `drink`, `go`, `no`, `yes`, `help`, `what`, `before`, with 15–21 signer IDs per gloss. Metadata plan has 199 instances / 49 unique signers; the estimate in bytes is unknown because the manifest stores no file sizes.
- Add optional local-video hand-landmark extraction and a simple sklearn baseline/evaluation/export scripts. Scripts must fail clearly when dependencies, authorized local video, or extracted features are absent; no dummy weights or scores.
- Gate: inspect and manifest scripts run against present metadata; landmark/training pipeline help and checks run. Actual training remains blocked until authorized clips and Python CV dependencies are supplied.

### P2 — Real browser recognition and validated coaching (blocked)
- Only after real training/evaluation: implement ONNX/TFJS parity and low-confidence/unknown outputs for supported labels; never infer phrase or full-ASL correctness from isolated-word classes.
- Face/Pose and component coaching require a sign-specific rubric, consent/rights and competent Deaf/ASL review. No face emotion score.
- Gate: signer-independent held-out metrics, model card, Python/browser parity, latency and expert-reviewed rubric. No existing assets meet this gate.

## Safe constraints

- Do not run the upstream all-class WLASL downloader or fetch YouTube-derived dataset clips. The checked-in safe downloader stays dry-run unless source rights are reviewed, hosts allowlisted, and size-probed. User-authorized policy: start <=2 GiB; hard total cap <=5 GiB. Dataset video access must fit source terms.
- Do not fetch ASL Citizen's 42.8 GB archive; require explicit user approval and confirm institutional/research compliance first.
- Keep raw videos, extracted features, generated weights and secrets ignored by Git. Do not upload or log user camera frames.
