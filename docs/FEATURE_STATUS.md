# SIGNTALK feature status

| Requested feature | Current status | What is actually implemented |
|---|---|---|
| ASL Vocabulary Learning | Starter scope available | Two Lifeprint/ASL University references (`Hello`, `Thank you`) with Indonesian guidance; both `in_review`, not SIGNTALK-approved. |
| Common ASL Phrases | Starter scope available | `Thank you` and `Nice to meet you`, with official YouTube embeds and links to source context. |
| AI Sign Recognition | **Unavailable** | Typed `SignRecognitionEngine` adapter returns `model_unavailable`. There is no trained sign classifier, dataset, label validation, or held-out evaluation. |
| Real-Time Visual Feedback | Tracking feedback available | MediaPipe 21-point overlay; guidance can say no hand, hand near frame edge, off-center, or too small. This evaluates framing/tracking only—not ASL correctness. |
| Face / body detection | Optional, detection-only toggles | Face oval and pose skeleton can be enabled locally. No facial expression or posture grading. |
| Interactive Mini Challenge | Available, unscored | Source → camera activation → landmark tracking → finish session. No classifier score is fabricated. |
| Final Challenge Evaluation | Available as an honest result | Stores a real session summary and reports `Belum dinilai`; no score until an evaluator exists. |
| Learning Progress Dashboard | Available, local | Read materials and completed camera sessions persist in browser storage and can be deleted. |

To make AI recognition real, the project still needs consented/licensed examples, an expert-reviewed label set, signer-independent training/test splits, a trained model, and measured accuracy/uncertainty. Hand tracking alone cannot supply these.
