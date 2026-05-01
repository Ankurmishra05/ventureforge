# VentureForge Benchmark Report

This report summarizes temporal holdout benchmark results on the Kaggle `Startup Investments` dataset after the first 730-day early-stage snapshot feature build.

## Task: exit

- Target column: `model_target_exit`
- Temporal split year: `2010`
- Train years: `1901-2010`
- Test years: `2011-2012`
- Best model by PR-AUC: `xgboost` with `0.0441`

### logistic_text

- Selected threshold: `0.08`
- ROC-AUC: `0.6721`
- PR-AUC: `0.0374`
- Brier score: `0.0157`
- Precision: `0.0674`
- Recall: `0.1342`
- F1: `0.0897`
- Predicted positive rate: `0.0316`

### hist_gradient_boosting

- Selected threshold: `0.08`
- ROC-AUC: `0.6852`
- PR-AUC: `0.0416`
- Brier score: `0.0157`
- Precision: `0.0811`
- Recall: `0.1039`
- F1: `0.0911`
- Predicted positive rate: `0.0203`

### xgboost

- Selected threshold: `0.08`
- ROC-AUC: `0.6856`
- PR-AUC: `0.0441`
- Brier score: `0.0155`
- Precision: `0.0901`
- Recall: `0.1299`
- F1: `0.1064`
- Predicted positive rate: `0.0228`

## Task: future_funding

- Target column: `model_target_future_funding`
- Temporal split year: `2010`
- Train years: `1901-2010`
- Test years: `2011-2012`
- Best model by PR-AUC: `xgboost` with `0.3211`

### logistic_text

- Selected threshold: `0.26`
- ROC-AUC: `0.822`
- PR-AUC: `0.2071`
- Brier score: `0.0692`
- Precision: `0.2139`
- Recall: `0.5574`
- F1: `0.3091`
- Predicted positive rate: `0.1729`

### hist_gradient_boosting

- Selected threshold: `0.26`
- ROC-AUC: `0.8458`
- PR-AUC: `0.3179`
- Brier score: `0.0561`
- Precision: `0.2364`
- Recall: `0.6174`
- F1: `0.3419`
- Predicted positive rate: `0.1732`

### xgboost

- Selected threshold: `0.27`
- ROC-AUC: `0.848`
- PR-AUC: `0.3211`
- Brier score: `0.0559`
- Precision: `0.2705`
- Recall: `0.5016`
- F1: `0.3514`
- Predicted positive rate: `0.123`

## Interpretation

- `future_funding` is currently the stronger supervised task and produces materially better PR-AUC than `exit`.
- Gradient boosting performs better than the linear text baseline on both tasks in the current temporal holdout.
- The tasks are imbalanced, so PR-AUC, recall, precision, and calibration are more useful than accuracy.
- These results should be treated as a baseline for iterative feature engineering, calibration, and model comparison.
