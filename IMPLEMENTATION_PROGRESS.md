# SIGNTALK — Implementation progress

## Baseline
- At initial scaffold audit, root contained only the design/prompt documents; no application or Git repository existed. A later audit discovered the supplied nested instruction package and `datasets/WLASL/`; these were preserved. No raw WLASL videos or trained weights are present.
- Design docs fully read. Content/review and model claims below remain constrained by the missing source material.

## Implemented
- React + TypeScript + Vite application with responsive design tokens/styles, React Router routes, and Tailwind CSS v4 plugin.
- PWA manifest, Workbox service worker, original SVG, Apple 180 PNG and generated 192/512 PNG icons. Large MediaPipe model/WASM assets are explicitly excluded from precache to avoid a huge install cache.
- Homepage: desktop R3F Canvas with original neutral hand geometry, communication ribbon, scroll-driven camera/group transforms, six DOM story beats, warmer palette, reduced-motion behavior, and a 2D mobile/low-power equivalent. No remote HDR environment is needed.
- Learning catalog search/category filtering and two source-linked vocabulary lessons plus two source-linked phrases. Each item is visibly `in_review`; its YouTube source plays via official embed.
- Vocabulary/phrase → source/context → camera Mini Challenge → ungraded final result → local progress. A typed `SignRecognitionEngine` adapter reports `model_unavailable`; no unsupported score is generated.
- Explicit camera activation, local MediaPipe Tasks Vision 0.10.35 hand tracking with 21-point overlay, plus optional local Face and Pose detection toggles. CPU tracking is rate-limited; frame guidance is based on hand bounds. No ASL recognition, face-expression, or body-posture grading is claimed.
- Browser-local reading IDs and actual practice-session metadata; result and progress show `Belum dinilai`, with deletion control.
- WLASL P1 tooling in `ai/`: read-only metadata audit, signer-group subset manifest, local-only landmark extraction, Logistic Regression baseline, held-out evaluation, and optional ONNX export. Metadata tooling runs; feature/training/export stages are blocked until authorized local clips, Python CV dependencies and extracted features exist.

## Not available / not claimed
- No SIGNTALK expert review, verified reuse license, local training videos/features, trained sign-classification model, or assessment engine exists. The four starter records cite ASL University/Lifeprint; that external source does not constitute SIGNTALK review. Classifier and linguistic evaluation remain unavailable.
- The automated camera smoke test uses Chrome's synthetic camera and detects no hand. The user-provided screenshot shows a real hand was detected once; independent overlay/rotation accuracy, varied signers, physical-device performance, Face/Pose detection on a person, and iPhone Safari remain unverified.
- PWA standalone manifest, SVG/PNG icon fetches, service-worker registration, and offline app-shell navigation are tested. Real Add-to-Home-Screen install and camera permission on iOS/Android devices are not yet verified; large vision assets are not precached.

## Commands / results
- `npm install` and development dependencies: completed. npm audit reported 6 vulnerabilities (2 low, 4 moderate) after package installation; review with `npm audit` before deployment.
- `npm run build`: passes TypeScript and production build; generated PWA manifest/service worker. Three.js is lazy-loaded and split into chunks capped below the 500 kB warning.
- `$env:SIGNTALK_BASE_URL='http://127.0.0.1:5177'; npm run test:browser`: passed on production preview in local Chrome. Verified desktop WebGL, six scroll beat counters, no scene-copy/scroll-cue overlap, vocabulary detail and phrase embeds, About on 360 px, widths 360/390/430/768/1024/1440, permission-denied handling, hand/face/pose task initialization (synthetic camera), session persistence, reduced-motion CTA, and WebGL/mobile 2D fallbacks.
- `python ai/scripts/inspect_dataset.py` and `python ai/scripts/prepare_subset.py --output <temp-path>`: passed. The local WLASL manifest has 2,000 classes / 21,083 instances; the metadata-only eight-class candidate has 15–21 signer IDs per gloss and signer-disjoint 60/20/20 splits (30 train / 11 val / 8 test signers). Feature transform smoke check passed. `ai/train.py` correctly refused training when no feature archive was provided.
- `python ai/scripts/download_wlasl_subset.py` dry run: 199 candidate metadata entries, 49 unique signers, 0 local clips, 59 YouTube URLs skipped, 140 other URLs not yet rights-verified; total byte estimate unavailable in metadata. Explicit HEAD-only probe on the 13 ASL Signbank URLs failed with `URLError`; no video was downloaded.
- `python -m unittest discover -s ai/tests -v`: 2 preprocessing unit tests passed (feature shape and missing-hand masks); not model-performance results.
- The synthetic camera intentionally contains no hand; expected detector state is `Tangan belum terlihat`. Physical hand detection/overlay alignment with a real signer and webcam remains unverified.
- Production preview on port 5177: manifest, worker, icon and app shell served; `npm run test:pwa` verified active service-worker registration and `/learn` navigation while offline. Large camera runtime assets are not precached, so offline camera use is not promised.
- Screenshots: `docs/qa-shots/desktop-{0,25,50,75,100}.png` and `docs/qa-shots/mobile-390.png`.
- `npm audit`: 6 reported vulnerabilities (2 low, 4 moderate); review and resolve before deployment.

## Next required work
1. Try the live camera with a physical webcam and signer; tune lighting/position guidance from real detection behavior and validate overlay alignment on iPhone Safari.
2. Test actual Add to Home Screen installation, icon masking and camera permission on iOS/Android devices; icon files and manifest checks are implemented.
3. Review 6 npm audit findings (2 low, 4 moderate) before deployment.
4. Complete SIGNTALK/Indonesian-context review and licensing review of the starter ASL sources before publishing the lessons as approved.
5. Add sign classification/evaluation only when a licensed dataset, trained model, preprocessing contract and subject-independent evaluation exist.
