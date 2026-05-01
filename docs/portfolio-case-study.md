# VentureForge Portfolio Case Study

## Problem

The goal was to move VentureForge from a prompt-based startup idea app into a defensible machine learning project with real data, temporal validation, calibrated probabilities, and measurable business-style prediction tasks.

## Dataset

- Source: Kaggle `Startup Investments` dataset based on a Crunchbase snapshot
- Unit of analysis: company
- Raw structure: multi-table startup event data including organizations, funding rounds, acquisitions, IPOs, and investments
- Processed feature table: `data/processed/startup_company_features.csv`
- Early-stage snapshot: first 730 days after founding

## Prediction Tasks

- `future_funding`: whether a startup receives funding after the early-stage snapshot window
- `exit`: whether a startup eventually reaches acquisition or IPO

## Modeling Approach

- Temporal train/test split using `founded_year`
- Validation-era threshold tuning instead of a fixed 0.5 threshold
- Post-hoc probability calibration comparison across raw, sigmoid, and isotonic methods
- Benchmarks: text-aware logistic regression, gradient boosting, and XGBoost

## Best Results

- Best `future_funding` model: `xgboost`
- ROC-AUC: `0.848`
- PR-AUC: `0.3211`
- Precision: `0.2705`
- Recall: `0.5016`
- F1: `0.3514`
- Threshold: `0.27`

- Best `exit` model: `xgboost` with PR-AUC `0.0441`

## Calibration Findings

- Selected calibration method for the best future-funding model: `isotonic`
- Validation Brier scores:
- `raw`: `0.0813`
- `sigmoid`: `0.0787`
- `isotonic`: `0.0759`

Top holdout calibration bins from the best future-funding model:
- predicted `0.1766`, observed `0.1139`
- predicted `0.2803`, observed `0.1691`
- predicted `0.4961`, observed `0.335`

## Slice Analysis

Example category slices from the best future-funding model:
- `web`: rows `2295`, positive rate `0.0314`, precision `0.3488`, recall `0.2083`
- `software`: rows `2046`, positive rate `0.0582`, precision `0.2317`, recall `0.3193`
- `ecommerce`: rows `1456`, positive rate `0.0453`, precision `0.2262`, recall `0.2879`
- `mobile`: rows `1201`, positive rate `0.0783`, precision `0.2612`, recall `0.3723`
- `other`: rows `1133`, positive rate `0.0141`, precision `0.5833`, recall `0.4375`

## What This Demonstrates

- Real multi-table feature engineering from messy startup event data
- Point-in-time target construction with leakage-aware evaluation
- Benchmark comparison across linear and tree-based models
- Threshold tuning and probability calibration for imbalanced classification
- Slice-based performance analysis instead of relying on a single accuracy number

## Next Steps

- Add SHAP-based local explanations for the serving model
- Train on richer text features such as sentence embeddings
- Connect predictions and explanations to the product UI