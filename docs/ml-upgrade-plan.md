# VentureForge ML/DS Upgrade Plan

## What changed

This repository now has the minimum components needed to justify an ML/DS framing:

- A labeled benchmark dataset in `data/startup_benchmark.jsonl`
- A reproducible supervised baseline model in `backend/scripts/train_viability_model.py`
- Offline metrics saved to `backend/model_artifacts/startup_viability_metrics.json`
- A model-assisted inference signal exposed through the decision stage

## Why this matters

The original project was an LLM application with no real dataset, no training loop, and no measurable offline evaluation. The new baseline turns it into a hybrid system:

- LLMs produce structured qualitative outputs
- A supervised model predicts verdict and risk score from `idea + audience`
- The decision agent can use the baseline prediction as an additional signal

## How to run

1. Install backend dependencies.
2. Train the baseline model:

```bash
python backend/scripts/train_viability_model.py
```

3. The training script writes:

- `backend/model_artifacts/startup_viability.joblib`
- `backend/model_artifacts/startup_viability_metrics.json`

## Current baseline

On the current 30-example seed benchmark, the first baseline produced:

- Accuracy: `0.50`
- Risk-score MAE: `13.45`

These numbers are not strong yet, which is fine. They establish a measurable baseline and make the repo suitable for iterative improvement, ablation work, and error analysis.

## How to present this on a CV

Use language like:

- Built a hybrid LLM + supervised-learning pipeline for startup viability scoring using FastAPI, PostgreSQL, and Next.js.
- Created a labeled benchmark dataset and trained a TF-IDF + logistic regression baseline to predict build/pivot/avoid verdicts and risk scores.
- Added reproducible offline evaluation for classification accuracy and risk-score MAE, then exposed model-assisted signals in the API decision layer.

Avoid claiming:

- production-grade market intelligence
- large-scale data science
- state-of-the-art modeling

## Strong next steps

- Grow the benchmark with 200-1000 manually reviewed examples
- Add annotation guidelines and inter-annotator agreement
- Replace placeholder market context with cited retrieval from real sources
- Log prompt/model versions with experiment metadata
- Add calibration plots, confusion matrices, and error slices by domain
- Add ranking or forecasting models using real startup outcome data
