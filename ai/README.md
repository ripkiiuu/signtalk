# SIGNTALK ASL research pipeline

The pipeline consumes **only local authorized clips**. It never downloads dataset videos. WLASL C-UDA and Microsoft ASL Citizen terms are summarized in `docs/DATASET_GUIDE.md`; obtain supervisor/institutional authorization before acquiring clips.

## Reproducible command sequence (PowerShell, Python 3.12)

```powershell
cd "D:\ABOUT PRIMA\PKM\SIGNTALK"
python --version
python -m pip install -r ai/requirements.txt
python ai/scripts/inspect_dataset.py
python ai/scripts/plan_wlasl_subset.py
python ai/scripts/download_wlasl_subset.py
python ai/scripts/prepare_subset.py --output datasets/processed/wlasl_8_signer_split.json --seed signtalk-wlasl-v1
```

The first planning commands are offline/read-only. The downloader is dry-run only by default. Never use the upstream all-class `datasets/WLASL/start_kit/video_downloader.py`. To request direct-file size probes/downloads, first review C-UDA, host rights and PKM-KC terms; pass exact allowlisted hosts and `--rights-confirmed`. Review the saved `--probe-sizes --probe-output` report before a separate `--download --size-plan` command. That command requires a size cap (recommend <=2 GiB initially; hard cap 5 GiB). YouTube URLs are skipped by the safe subset utility.

Current local run: the ASL Citizen six-class pilot has 184 licensed research clips under the ignored `datasets/raw/asl_citizen/` path and extracted features under `datasets/processed/`. These files remain local under Microsoft Research terms. To reproduce preprocessing:

```powershell
python ai/scripts/extract_landmarks.py `
  --manifest datasets/raw/asl_citizen/subset_manifest.json `
  --video-root datasets/raw/asl_citizen/videos `
  --output datasets/processed/asl_citizen_6class_hand_features.npz
```

The extractor samples a bounded sequence and records MediaPipe hand coordinates/masks with class, signer and **project signer-group split** metadata. It does not store/ upload SIGNTALK user webcam frames. The baseline only sees external dataset clips copied into the ignored raw-data area with authorization.

```powershell
python ai/train.py --features datasets/processed/asl_citizen_6class_hand_features.npz --output models/asl_citizen_6class_hand_logreg.joblib --include-validation
python ai/evaluate.py --features datasets/processed/asl_citizen_6class_hand_features.npz --model models/asl_citizen_6class_hand_logreg.joblib --split test --output ai/reports/asl_citizen_6class_test.json
python -m pip install -r ai/requirements-export.txt
python ai/export.py --features datasets/processed/asl_citizen_6class_hand_features.npz --model models/asl_citizen_6class_hand_logreg.joblib --output models/asl_citizen_6class_hand_logreg.onnx --parity-samples 64
```

The current v2 model uses the official train+validation participants (112 clips / 29 signers) for final fitting. The test split (72 clips / 11 signers) remains signer-disjoint and held out. Export parity is checked on 64 feature samples. The ONNX file stays local and can be loaded manually in PWA practice; it is never bundled or uploaded.

## Baseline scope and limitations

- The current baseline is isolated-word ASL Citizen gloss classification, not phrase/grammar recognition.
- Training refuses signer overlap between fit and test samples. `--include-validation` is intended only for final refit after model selection; the test signers remain held out.
- Hand coordinates are normalized image coordinates; this is not an ASL expert rubric and is not facial/body assessment.
- Current v2 held-out metrics: accuracy 83.3%, macro-F1 83.5% (72 clips / 11 signers), modestly above v1. These scores are not calibrated probabilities and do not validate a particular learner attempt. Live-camera/domain errors remain expected.
- Keep `datasets/raw/`, `datasets/processed/`, and generated model weights local; root `.gitignore` excludes them.
