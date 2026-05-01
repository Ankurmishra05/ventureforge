# Startup Data Pipeline

## Dataset choice

This pipeline targets the Kaggle `Startup Investments` dataset, a Crunchbase 2013 snapshot with organizations, funding rounds, acquisitions, IPOs, and related tables.

Sources:

- Kaggle dataset: https://www.kaggle.com/datasets/justinas/startup-investments
- Crunchbase CSV export overview: https://support.crunchbase.com/hc/en-us/articles/25568542362771-FAQ-What-files-are-included-in-CSV-Export

## Ingestion goal

The raw dataset is multi-table and entity-centric. This script converts it into a single company-level feature table suitable for:

- exit prediction
- startup outcome classification
- funding trajectory analysis
- tabular + text ML experiments

## Current output

`backend/scripts/prepare_startup_dataset.py` writes:

- `data/processed/startup_company_features.csv`

Current derived fields include:

- organization metadata: name, category, geography, founding date
- funding aggregates: number of rounds, total raised, average round size, participant counts
- early-stage funding aggregates from the first 730 days after founding
- investor aggregates: total investment rows and unique investor count
- acquisition aggregates: acquisition flags, dates, and max price
- IPO aggregates: IPO flags, dates, and valuation/raised amounts
- engineered features: company age, time to first round, round-span duration, description length
- modeling flags and labels: `snapshot_available`, `model_target_exit`, `model_target_funded`, `successful_exit`, `outcome_label`

## Modeling workflow

`backend/scripts/train_exit_model.py` trains a binary classifier to predict whether a startup eventually reaches a successful exit using only early-stage signals:

- first-two-year funding behavior
- company description text
- founding year
- category and geography

The training script:

- filters to rows with a valid early-stage snapshot
- uses a temporal split by `founded_year`
- trains a logistic regression baseline with numeric, categorical, and TF-IDF text features
- writes a model artifact, a JSON metrics report, and holdout predictions

Artifacts:

- `backend/model_artifacts/startup_exit_model.joblib`
- `backend/model_artifacts/startup_exit_metrics.json`
- `backend/model_artifacts/startup_exit_holdout_predictions.csv`

## Benchmark workflow

`backend/scripts/train_outcome_benchmarks.py` is the stronger DS evaluation entrypoint.

It trains benchmark models for:

- `exit`: eventual acquisition or IPO
- `future_funding`: whether the company raises funding after the first 730 days

It compares:

- `logistic_text`: logistic regression with tabular features plus TF-IDF description text
- `hist_gradient_boosting`: tabular gradient boosting baseline

It also adds:

- threshold selection on a validation-era split instead of a fixed `0.5`
- PR-curve artifacts
- calibration bins
- slice-based error analysis for category, country, and founded-year buckets

Artifacts are written under:

- `backend/model_artifacts/<task>/<model>/metrics.json`
- `backend/model_artifacts/<task>/<model>/pr_curve.csv`
- `backend/model_artifacts/<task>/<model>/holdout_predictions.csv`
- `backend/model_artifacts/<task>/<model>/slice_analysis.json`
- `backend/model_artifacts/benchmark_summary.json`

## Why this is better for ML/DS roles

This moves the project from prompt orchestration to real data engineering:

- multi-table joins
- schema normalization
- feature engineering from transactional startup data
- explicit target construction for supervised learning

## Next steps

- add probability calibration methods such as isotonic or Platt scaling
- compare LightGBM/XGBoost once the environment allows those dependencies
- add cross-validation inside the training era while preserving the temporal holdout
- add richer text representations such as sentence embeddings
- add EDA notebooks and data-quality validation
- connect the best model back into the product API for prediction and explanation
