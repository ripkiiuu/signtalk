# SIGNTALK dataset guide (research prototype)

## Findings in this workspace

- The project already contains `datasets/WLASL/start_kit/WLASL_v0.3.json` (about 12.3 MB) and the upstream WLASL source code/README.
- Manifest audit: 2,000 glosses / 21,083 metadata instances; `sorry` is present (14 instances). This does **not** mean the video clips are present or legally reusable in every context.
- Current metadata-only 8-class pilot (common concepts, 15–21 metadata signers per gloss): `who` (25 instances/21 signers), `drink` (35/18), `go` (26/17), `no` (22/18), `yes` (22/17), `help` (22/15), `what` (21/18), `before` (26/16). The classes have 199 manifest instance IDs / 49 unique signers. A 60/20/20 hash split gives 30/11/8 unique signers in train/validation/test. These are metadata counts, not playable/authorized clips; the test signer count remains small and any result exploratory.
- Those selected records contain 59 YouTube URLs and 140 URLs on other hosts; zero local clips. Of 13 old ASL Signbank URLs (the one candidate with an explicit non-commercial CC BY-NC-SA 4.0 reuse policy for non-draft clips), a HEAD-only size/reachability probe returned `URLError` for every URL. Draft status could not be verified, so they were not downloaded. Other sources include hosts whose policies prohibit AI/ML use or require separate permission (see below); the rest remain unverified.
- No video files, extracted features, or trained WLASL weights were found. Raw videos are absent. The supplied WLASL metadata reports 117/109/105 distinct signers in its train/val/test sets, but the sets overlap by signer (train-val 108; train-test 104; val-test 98). Do not claim signer-independent performance from those published splits.

## WLASL access conditions

- Official source: https://github.com/dxli94/WLASL and https://dxli94.github.io/WLASL/.
- The supplied repository states that WLASL is under the Computational Use of Data Agreement (C-UDA), academic/computational use only, no commercial use; its C-UDA also says the provider does not warrant that it owns all upstream rights. Read `datasets/WLASL/start_kit/C-UDA-1.0.pdf` and confirm institutional/PKM use with the project supervisor before acquiring or processing clips.
- The upstream downloader uses YouTube URLs/`yt-dlp`. SIGNTALK must **not** scrape/download those URLs without explicit rights/approval. YouTube lesson embeds remain separate from training data.
- Source policy check: Handspeak's current terms prohibit using/downloading content for AI/ML; Signing Savvy prohibits copying/embedding without permission; SpreadTheSign requires permission for research use. Those hosts are not approved as training sources. ASL Signbank's terms allow non-commercial CC BY-NC-SA reuse and direct video saving with attribution, but old WLASL URLs did not answer the authorized size probe and draft status is unknown.
- No video body was downloaded. The safe downloader's metadata-only plan was run; one source-specific HEAD probe was attempted for the 13 ASL Signbank URLs and failed for all 13. No YouTube or unverified-host probe/download was made.

## ASL Citizen alternative

- Official page: https://www.microsoft.com/en-us/research/project/asl-citizen/.
- Microsoft Download Center lists `ASL_Citizen.zip` at 42.8 GB. Microsoft Research's license is for non-commercial, non-revenue research use, prohibits redistribution of data or modifications, and requires use consistent with participant consent. The datasheet says the archive is publicly downloadable; that is not permission to redistribute it or use it commercially.
- **Not downloaded**: the full archive exceeds the user's 5 GB cap; the official distribution is a single 42.8 GB archive, not a selected-class download. Do not download it. Do not check it into Git.

## ASL Signbank metadata alternative

- Downloaded the official ECV index only: `datasets/ASLSignBank/asl.ecv` (1,149,253 bytes, 4,528 gloss entries). It contains gloss/translation metadata and external entry references, not video bytes or signer IDs; it cannot by itself train a recognizer or support signer-independent splits.
- Official terms: https://aslsignbank.com/about/conditions/ allow reuse of non-draft videos under CC BY-NC-SA 4.0 with attribution/direct source links for non-commercial use.
- WLASL's 13 legacy Signbank URLs use the old `aslsignbank.haskins.yale.edu` host. A HEAD-only size/reachability probe returned `URLError` for all 13; no clips were downloaded. Since draft status is absent from WLASL metadata, those particular clips remain unusable until an accessible official entry and non-draft status are confirmed.
- The new ECV index lacks signer IDs. Do not treat separate gloss entries as separate signers; signer identity/consent evidence is needed before a subject-independent model evaluation.

## Safe local workflow

1. Confirm institutional/PKM authorization and the relevant dataset terms.
2. Acquire only an approved subset by the dataset's official means. Put derived/authorized clips in `datasets/raw/wlasl/videos/` (ignored by root `.gitignore`). Keep raw files local; do not upload participant frames.
3. `python ai/scripts/inspect_dataset.py` audits only the local manifest and reports which clip files are missing; it never downloads anything.
4. `python ai/scripts/plan_wlasl_subset.py` reports class instances, signer counts, source hosts, storage destination, and why the byte estimate cannot be derived from metadata. It makes no network requests.
5. `python ai/scripts/download_wlasl_subset.py` is dry-run only by default and filters the selected classes. YouTube is always skipped. `--probe-sizes` requires `--rights-confirmed` and per-host `--allow-host`; it saves a reviewable size plan. A separate `--download --size-plan ...` command requires known Content-Length values, a user-supplied cap (recommend <=2 GiB initially; hard cap 5 GiB), and the same class/URL/host fingerprint. A size probe was attempted for 13 ASL Signbank candidates and all failed; no video was downloaded. CLI flags do not replace source-rights review.
6. `python ai/scripts/prepare_subset.py --output datasets/processed/wlasl_subset.json` creates a deterministic eight-gloss manifest and assigns all samples from a signer to one project split. It uses signer IDs, not the overlapping upstream split labels.
7. Install optional dependencies with `python -m pip install -r ai/requirements.txt`; extract hand landmarks from the already-local/preprocessed clips with `python ai/scripts/extract_landmarks.py --manifest datasets/processed/wlasl_subset.json --video-root datasets/raw/wlasl/videos --output datasets/processed/wlasl_hand_landmarks.npz`.
8. Train/evaluate/export only after real clips and features exist. See `ai/README.md`; scripts refuse to create results when the inputs are missing.

The initial baseline is isolated-word, hand-landmark classification. It cannot validate phrases, ASL grammar, regional variants, facial/non-manual markers, or generalize beyond the tested signer split without additional validated data.
