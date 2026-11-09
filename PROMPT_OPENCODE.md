# OPENCODE MASTER EXECUTION PROMPT — SIGNTALK 3D PWA

> Paste the following into OpenCode **from the SIGNTALK project root**, with `desain.md` beside it. The model must read the spec as a contract and preserve source truth. This file is an execution prompt, not a claim that anything has already been implemented.

## YOUR ROLE

Act as a principal creative frontend engineer, senior Three.js / React Three Fiber developer, React/TypeScript PWA architect, senior camera/computer-vision engineer, accessibility specialist, and scientific ML integration reviewer.

**Project:** SIGNTALK — interactive American Sign Language learning PWA for Indonesian Deaf users interested in ASL, developed as a PKM-KC prototype.

**Primary objective:** Implement a genuinely excellent, immersive, accessible, interactive PWA. The homepage has a **real Three.js 3D scroll-driven experience**; the learning, camera practice, assessment, and progress flows are functional and scientifically honest. No generic AI-made dashboard. No nonfunctional AI demo.

## STRICT PRE-FLIGHT

1. Read `desain.md` **completely**, and read user-supplied concept files if present. The `desain.md` in the root is the authoritative design and acceptance specification.
2. Inspect current project (`pwd`, files, package manifests, git status, dependencies and existing assets). Do NOT delete, reset, or recreate an existing implementation without necessity; never destroy uncommitted changes.
3. If empty folder, initialize one Vite + React + TypeScript project in **the current folder**, not in another nested folder. Use Tailwind if compatible with setup; set up React Router or another maintained routing solution.
4. Record actual baseline in `IMPLEMENTATION_PROGRESS.md` (verified existing features, assets, missing model/dataset, unresolved decisions). Do not invent users, validated videos or recognition accuracy.
5. Choose stable compatible package versions. `@react-three/fiber` major must match React major; avoid untested alpha APIs. Use official current docs to confirm `@react-three/drei`, Three.js, and R3F compatibility.
6. Create a safe branch/backup if Git available. Do not ask user for basic design decisions already specified; start working.

## THE ONLY ACCEPTABLE DESIGN DIRECTION

- **The Language of Motion:** calm premium educational UI with real-time interactive elements, confident typography, forest/deep-navy/teal/mint accent palette, generous but not empty spacing, readable 16–18 px body text.
- Authentic original 3D scenes and coherent motion from one visual world, **not** rotating cubes, flat cards with CSS transforms, video background, random particles, or reused medical/florist 3D props.
- Real 3D geometry with purposeful camera motion triggered by page scrolling and scene changes.
- 3D objects must match SIGNTALK's identity: abstract communication ribbons, neutral anatomical hands, instructional stage, learning spaces and landmark explanations. **Do not fabricate a specific ASL sign in the 3D avatar.**
- Accessibility first: the UI is useful without sound, includes Indonesian text guidance, respects reduced motion, avoids color-only feedback and keeps keyboard/touch interactions working.
- Aesthetic quality is judged by actual rendered screenshots/video and usability, not by fancy CSS class names or ‘premium’ in the report.

## NON-NEGOTIABLE UI / ROUTES

Implement routes in the existing codebase, or equivalent:

- `/` — 3D editorial learning journey (6 scenes).
- `/learn` — vocabulary categories/search/filter.
- `/learn/:slug` — lesson with verified-source video/illustration, Indonesian explanation, practice status.
- `/phrases` and `/phrases/:slug` — common ASL phrases using official YouTube iframe with relevant context; do not rip videos.
- `/practice/:lessonId` — camera permission/preflight, live hand tracking, honest feedback, challenge flow.
- `/challenge/:lessonId/result/:attemptId` — final evaluation of actual attempt; unknown/unavailable states.
- `/progress` — real persisted learner progress, not dummy statistics.
- `/account` — settings/privacy (simple local profile or true account if implemented).
- `/about` — scope, data/privacy and method explanation.

Implement polished states for empty, loading, permission-denied, no camera, WebGL missing, unknown sign, model missing, offline/YouTube unavailable.

## PHASE 1 — FUNCTIONAL APP SHELL

- Build theme tokens, typography, accessible responsive navigation, proper mobile safe areas.
- Establish typed lesson schema, curriculum categories and phrase metadata derived from user concept. **Do not invent authoritative ASL instruction or pretend material is expert-approved.**
- Implement data model with `reviewStatus`, `source`, `aiSupportStatus` and asset licensing fields. For content missing verified media, show explicit placeholders with useful learning context, not fake lessons.
- Implement navigation, lesson selection, video embed view, easy-to-use learning progress that works with browser-local persistence.
- Configure Vite PWA plugin, manifest, offline/online states, update mechanism. Test actual production build and preview.
- Keep the page usable on iPhone Safari.

## PHASE 2 — REAL THREE.JS SCROLL EXPERIENCE

Use Three.js + React Three Fiber + compatible Drei. GSAP ScrollTrigger is allowed if justified. Build a **working visual prototype first** and inspect it before expanding.

### Required scenes

1. **The Opening Gesture:** physically dimensional stage, abstract communication ribbon, neutral anatomical hand that does NOT purport to represent a specific sign; hero CTA clearly readable and functional.
2. **Vocabulary Universe:** floating dimensional learning modules for Alphabet, Numbers, Greetings, Family etc. with real click targets to lesson categories.
3. **Demonstration Studio:** camera approaches a virtual space; real DOM video preview/player overlay and context label, not video texture-only controls.
4. **Landmark Theater:** visible 3D landmarks / conceptual hand skeleton demonstrating how computer vision estimates points, explicitly marked an illustration.
5. **Feedback Space:** visually distinct tracking vs sign classification vs component assessment, with transparent status labels.
6. **Learning Path:** progress-inspired 3D composition leading to functional learning dashboard CTA.

### Measurable Three.js conditions

- There must be a real Canvas, camera, 3D mesh(es), lights, renderer, world transforms.
- Camera position/target or equivalent 3D world navigation MUST change continuously along actual scroll progress; not only DOM fades or CSS-only parallax.
- Use an orthographic/isometric camera or similarly controlled cinematic composition; shadows/materials are art-directed.
- Cross-device responsiveness: hero not overlapped by navbar, no cropped CTA, no horizontal page overflow.
- Lazy-load 3D scenes/assets, cap DPR, dispose resources, optimize on mobile.
- If GPU unavailable, show an intentionally designed 2D version; NEVER simply hide the bug or show raw “WebGL unavailable” text in the finished UI.
- On regular supported desktop Chrome/Edge, must verify that renderer initializes and actual geometry appears, and inspect console/network errors.
- Browser screenshots at scroll 0/25/50/75/100% are required. Do not claim completion without showing the scene/camera variations. If browser automation has no GPU, distinguish environment limitation from app failure and give a concrete user-side validation process.
- Reduced-motion renders complete content with minimal/no camera travel.
- 3D hand explorer is optional in first phase, but any 3D hand representations must be honest about whether they are educational/validated.

## PHASE 3 — CAMERA + MEDIAPIPE: REAL INPUT

Implement through standard HTTPS browser media APIs and `@mediapipe/tasks-vision` compatible APIs:

- An explicit `Aktifkan Kamera` click triggers permission. Never initiate camera during landing scrolling.
- Handle denied permission, unavailable webcam, missing HTTPS secure context, bad lighting and missing hands.
- Render real video and overlay actual detected landmarks (21 per hand); map coordinates correctly, including mirror/handedness. Never draw arbitrary fake dots for live practice.
- Build explicit states: `idle -> requesting -> preview -> tracking -> recording/practicing -> processing -> result -> error` with pause/stop/cancel.
- Stop media tracks when leaving; do not record/upload face/body video by default.
- Use performance-safe inference; run at a bounded rate, skip stale frames, avoid main-thread blocking where supported. If Web Workers path is incompatible with the chosen vision/video APIs on the test device, state limitations and use a measured adaptive main-thread path.
- Enable Face/Pose only for gestures requiring nonmanual features and only when validated and performant; no need to run all heavy detectors for every lesson.
- Do not run decorative Three.js scenes concurrently on low-power camera sessions.

**Critical:** MediaPipe gives landmarks, not linguistic correctness; do not use confidence of detection as sign correctness.

## PHASE 4 — HONEST AI RECOGNITION INTEGRATION

- Search the actual repository for dataset, model weights, training notebooks, label map, preprocessing and inference files.
- If there is a REAL trained compatible model, validate input schema, outputs, class map, preprocessing equivalence, version, and use it; run smoke test and record limitations.
- If NO trained model exists, implement typed `SignRecognitionEngine` / `AssessmentEngine` adapters and clear `model_unavailable` UI. Do **not** invent model predictions, simulated class accuracy, fake score 85/100, green/red per-joint judgement, or claim the BiLSTM is trained.
- Optional: create a clearly separated, labeled tech demo (e.g. tracking demo) without pretending that class recognition is solved.
- Offer a reproducible ML training/evaluation pipeline or scaffold using actual authorized data. BiLSTM is a candidate, not a mandatory network. Establish classical/simple baselines; subject-independent split and macro-F1/confusion matrix required. No fabricated metrics.
- Restrict AI class availability to trained/verified labels; show learning-only mode for the rest of curriculum.

## PHASE 5 — FEEDBACK + MINI CHALLENGE + FINAL EVALUATION

- Mini Challenge flow follows Learn → Watch → Practice → Real-time Feedback → Final Evaluation.
- Camera tracking feedback (e.g. `hand not centered`) is distinct from ASL validity feedback.
- Real-time feedback uses actual evaluator outputs. If attribute evaluators absent, show `Belum dinilai` instead of red/green 'wrong/right'.
- Any score must derive from a documented, validated formula; never use classifier probability as a substitute for percent-correct gesture.
- Results can show `recognized`, `uncertain`, `incomplete`, `not_supported`, `camera_error` and real component statuses.
- Save only actual attempt metadata and user-approved results; allow retries; progress counts real completed content and attempts, not manufactured progress.
- Include a user-friendly explanation of uncertainty and respect legitimate signing variation.

## PHASE 6 — USER-DATA, ACCESSIBILITY, RESEARCH QUALITY

- Default privacy: local processing, no raw video storage/upload or passive camera recording.
- Only persist allowed user progress; user can delete it. If account sync added, use auth/authorization/RLS, never public keys with privileged permissions.
- Source and status tags for ASL materials; allow future ASL-expert review workflow; do not manufacture validation credentials.
- Accessible captions, visual affordances, focus states, keyboard controls, contrast AA, descriptive feedback beyond green/red, reduced-motion, touch hit areas.
- Test realistic iPhone Safari interactions, desktop browser, webcam missing, WebGL unavailable, online/offline.

## TEST AND VERIFY — DO NOT CLAIM WHAT YOU DID NOT TEST

Run and record:

1. `npm install` using compatible packages, build scripts, TypeScript checks and lint where present.
2. `npm run build` and preview deploy check; PWA manifest/service worker scope and installability.
3. Route navigation, all CTAs, lesson search/filter, phrase embeds or honest unavailable states.
4. WebGL detection + Canvas init + actual geometry and camera motion (use screenshot per scene if possible).
5. Permission denied and successful camera detection where hardware available.
6. Actual landmark overlay alignment; lifecycle cleanup; correct status distinctions.
7. Attempt persistence, empty-state and unsupported AI state.
8. Mobile layout at 360, 390, 430, 768, 1024, 1440 widths. Check browser console and visual output.
9. Reduced motion/no WebGL fallback; no page breakage.
10. No invented datasets, model metrics, expert validation, gesture scores or copyrighted mirrored videos.

In `IMPLEMENTATION_PROGRESS.md` document: actual files changed, phases completed, commands/results, model readiness, video content readiness, issues, required real assets, and untested iPhone device concerns.

## IMPORTANT QUALITY GATE

The project is NOT complete if the homepage consists of a big headline plus static cards and a rotating 3D object. It is NOT complete if a WebGL fallback message appears on normal supported browsers. It is NOT complete if buttons show dummy data and fake model outputs.

**Succeed visually:** 6-scene connected 3D learning journey with visible camera movement and excellent responsive typography.

**Succeed functionally:** content discovery → real video source/context → honest camera tracking → supported AI result or explicit unavailable state → saved progress.

**Succeed scientifically:** explicit separation between hand detection, ASL classification, and validated pedagogical assessment.

Start working in the existing folder. Do not stop after writing a plan; implement in working phases. If some phases cannot be completed due to missing assets/model or tool limits, make truthful fallbacks, preserve completed work, and report exact blockers. Never label a model-generated mockup as a working recognition system.
