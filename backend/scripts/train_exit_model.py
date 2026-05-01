import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_PATH = REPO_ROOT / "data" / "processed" / "startup_company_features.csv"
ARTIFACT_DIR = REPO_ROOT / "backend" / "model_artifacts"
MODEL_PATH = ARTIFACT_DIR / "startup_exit_model.joblib"
METRICS_PATH = ARTIFACT_DIR / "startup_exit_metrics.json"
PREDICTIONS_PATH = ARTIFACT_DIR / "startup_exit_holdout_predictions.csv"

TARGET_COLUMN = "model_target_exit"
TIME_COLUMN = "founded_year"
SNAPSHOT_FLAG_COLUMN = "snapshot_available"

NUMERIC_FEATURES = [
    "founded_year",
    "description_length",
    "early_num_funding_rounds",
    "early_total_raised_usd",
    "early_avg_raised_usd",
    "early_max_raised_usd",
    "early_avg_participants",
    "early_max_participants",
]

CATEGORICAL_FEATURES = [
    "category",
    "country",
    "state",
    "city",
    "early_latest_round_type",
]

TEXT_FEATURE = "description"


def flatten_text_column(values):
    return pd.Series(values.squeeze()).astype(str).to_numpy()


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {path}. Run prepare_startup_dataset.py first."
        )

    frame = pd.read_csv(path, low_memory=False)
    frame.columns = [str(column).strip() for column in frame.columns]
    return frame


def filter_modeling_frame(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame = frame[frame[SNAPSHOT_FLAG_COLUMN] == 1].copy()
    frame = frame[frame[TARGET_COLUMN].notna()].copy()
    frame[TARGET_COLUMN] = frame[TARGET_COLUMN].astype(int)
    frame[TIME_COLUMN] = pd.to_numeric(frame[TIME_COLUMN], errors="coerce")
    frame = frame[frame[TIME_COLUMN].notna()].copy()
    return frame


def build_temporal_split(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    sorted_frame = frame.sort_values(TIME_COLUMN).reset_index(drop=True)
    if len(sorted_frame) < 100:
        raise ValueError("Need at least 100 rows for a meaningful temporal split.")

    candidate_row_indices = list(
        range(int(len(sorted_frame) * 0.8), int(len(sorted_frame) * 0.6), -2500)
    )
    candidate_row_indices.extend(
        range(int(len(sorted_frame) * 0.82), min(len(sorted_frame) - 1, int(len(sorted_frame) * 0.9)), 2500)
    )

    seen_years = set()
    for row_index in candidate_row_indices:
        row_index = max(1, min(len(sorted_frame) - 2, row_index))
        split_year = int(sorted_frame.iloc[row_index][TIME_COLUMN])
        if split_year in seen_years:
            continue
        seen_years.add(split_year)

        train = frame[frame[TIME_COLUMN].astype(int) <= split_year].copy()
        test = frame[frame[TIME_COLUMN].astype(int) > split_year].copy()

        if train.empty or test.empty:
            continue
        if train[TARGET_COLUMN].nunique() < 2 or test[TARGET_COLUMN].nunique() < 2:
            continue
        if len(train) < 5000 or len(test) < 5000:
            continue

        return train, test, split_year

    raise ValueError(
        "Could not find a temporal split where both train and test contain both classes."
    )


def build_model() -> Pipeline:
    numeric_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="infrequent_if_exist",
                    min_frequency=100,
                ),
            ),
        ]
    )
    text_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value="")),
            (
                "flatten",
                FunctionTransformer(
                    flatten_text_column,
                    validate=False,
                    feature_names_out="one-to-one",
                ),
            ),
            ("tfidf", TfidfVectorizer(max_features=2000, ngram_range=(1, 2))),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_transformer, NUMERIC_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_FEATURES),
            ("text", text_transformer, [TEXT_FEATURE]),
        ]
    )

    return Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    solver="liblinear",
                ),
            ),
        ]
    )


def evaluate_binary_model(
    y_true: pd.Series,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
) -> dict:
    return {
        "positive_rate": round(float(np.mean(y_true)), 4),
        "predicted_positive_rate": round(float(np.mean(y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, y_prob)), 4),
        "pr_auc": round(float(average_precision_score(y_true, y_prob)), 4),
        "brier_score": round(float(brier_score_loss(y_true, y_prob)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(
            y_true,
            y_pred,
            output_dict=True,
            zero_division=0,
        ),
    }


def extract_top_coefficients(model: Pipeline, limit: int = 15) -> dict:
    classifier = model.named_steps["classifier"]
    preprocessor = model.named_steps["preprocessor"]
    feature_names = preprocessor.get_feature_names_out().tolist()
    coefficients = classifier.coef_[0]

    paired = list(zip(feature_names, coefficients))
    top_positive = sorted(paired, key=lambda item: item[1], reverse=True)[:limit]
    top_negative = sorted(paired, key=lambda item: item[1])[:limit]

    return {
        "top_positive_features": [
            {"feature": name, "coefficient": round(float(weight), 4)}
            for name, weight in top_positive
        ],
        "top_negative_features": [
            {"feature": name, "coefficient": round(float(weight), 4)}
            for name, weight in top_negative
        ],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Train a temporal startup exit prediction model from company-level features."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Path to the processed startup feature table.",
    )
    args = parser.parse_args()

    frame = filter_modeling_frame(load_dataset(args.input))
    train_frame, test_frame, split_year = build_temporal_split(frame)

    x_train = train_frame[NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TEXT_FEATURE]]
    x_test = test_frame[NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TEXT_FEATURE]]
    y_train = train_frame[TARGET_COLUMN]
    y_test = test_frame[TARGET_COLUMN]

    model = build_model()
    model.fit(x_train, y_train)

    test_probabilities = model.predict_proba(x_test)[:, 1]
    test_predictions = (test_probabilities >= 0.5).astype(int)

    metrics = {
        "dataset_path": str(args.input),
        "task": "predict_successful_exit_from_early_stage_signals",
        "target_column": TARGET_COLUMN,
        "train_rows": int(len(train_frame)),
        "test_rows": int(len(test_frame)),
        "temporal_split_year": int(split_year),
        "train_year_range": [
            int(train_frame[TIME_COLUMN].min()),
            int(train_frame[TIME_COLUMN].max()),
        ],
        "test_year_range": [
            int(test_frame[TIME_COLUMN].min()),
            int(test_frame[TIME_COLUMN].max()),
        ],
        "features": {
            "numeric": NUMERIC_FEATURES,
            "categorical": CATEGORICAL_FEATURES,
            "text": TEXT_FEATURE,
        },
        "metrics": evaluate_binary_model(y_test, test_predictions, test_probabilities),
    }
    metrics.update(extract_top_coefficients(model))

    holdout_predictions = test_frame[
        ["org_id", "name", "founded_year", "category", TARGET_COLUMN]
    ].copy()
    holdout_predictions["predicted_exit_probability"] = test_probabilities
    holdout_predictions["predicted_exit_label"] = test_predictions

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "model_version": "startup-exit-logreg-temporal-v1",
            "target_column": TARGET_COLUMN,
            "temporal_split_year": int(split_year),
            "numeric_features": NUMERIC_FEATURES,
            "categorical_features": CATEGORICAL_FEATURES,
            "text_feature": TEXT_FEATURE,
        },
        MODEL_PATH,
    )
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    holdout_predictions.to_csv(PREDICTIONS_PATH, index=False)

    print(f"Saved model artifact to {MODEL_PATH}")
    print(f"Saved metrics to {METRICS_PATH}")
    print(f"Saved holdout predictions to {PREDICTIONS_PATH}")
    print("Holdout ROC-AUC:", metrics["metrics"]["roc_auc"])
    print("Holdout PR-AUC:", metrics["metrics"]["pr_auc"])
    print("Holdout F1:", metrics["metrics"]["f1"])


if __name__ == "__main__":
    main()
