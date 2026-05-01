import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, OrdinalEncoder, StandardScaler

try:
    from xgboost import XGBClassifier
except ImportError:  # pragma: no cover
    XGBClassifier = None


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_PATH = REPO_ROOT / "data" / "processed" / "startup_company_features.csv"
ARTIFACT_DIR = REPO_ROOT / "backend" / "model_artifacts"

TIME_COLUMN = "founded_year"
SNAPSHOT_FLAG_COLUMN = "snapshot_available"
TARGET_OPTIONS = {
    "exit": "model_target_exit",
    "future_funding": "model_target_future_funding",
}

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
SLICE_COLUMNS = ["category", "country"]


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


def filter_modeling_frame(frame: pd.DataFrame, target_column: str) -> pd.DataFrame:
    frame = frame.copy()
    frame = frame[frame[SNAPSHOT_FLAG_COLUMN] == 1].copy()
    frame = frame[frame[target_column].notna()].copy()
    frame[target_column] = frame[target_column].astype(int)
    frame[TIME_COLUMN] = pd.to_numeric(frame[TIME_COLUMN], errors="coerce")
    frame = frame[frame[TIME_COLUMN].notna()].copy()
    return frame


def build_temporal_split(frame: pd.DataFrame, min_rows: int) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    sorted_frame = frame.sort_values(TIME_COLUMN).reset_index(drop=True)
    candidate_row_indices = list(
        range(int(len(sorted_frame) * 0.8), int(len(sorted_frame) * 0.6), -2500)
    )
    candidate_row_indices.extend(
        range(
            int(len(sorted_frame) * 0.82),
            min(len(sorted_frame) - 1, int(len(sorted_frame) * 0.9)),
            2500,
        )
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
        if train.iloc[:, 0].empty or test.iloc[:, 0].empty:
            continue
        if train.iloc[:, 0].shape[0] < min_rows or test.iloc[:, 0].shape[0] < min_rows:
            continue

        return train, test, split_year

    raise ValueError("Could not create a valid temporal split.")


def build_train_validation_split(frame: pd.DataFrame, target_column: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    sorted_frame = frame.sort_values(TIME_COLUMN).reset_index(drop=True)
    candidate_row_indices = list(
        range(int(len(sorted_frame) * 0.8), int(len(sorted_frame) * 0.6), -2000)
    )
    seen_years = set()

    for row_index in candidate_row_indices:
        row_index = max(1, min(len(sorted_frame) - 2, row_index))
        split_year = int(sorted_frame.iloc[row_index][TIME_COLUMN])
        if split_year in seen_years:
            continue
        seen_years.add(split_year)

        train = frame[frame[TIME_COLUMN].astype(int) <= split_year].copy()
        validation = frame[frame[TIME_COLUMN].astype(int) > split_year].copy()
        if train.empty or validation.empty:
            continue
        if train[target_column].nunique() < 2 or validation[target_column].nunique() < 2:
            continue
        return train, validation

    raise ValueError("Could not create a valid train/validation temporal split.")


def build_logistic_model() -> Pipeline:
    numeric_transformer = Pipeline(
        [("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
    )
    categorical_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "onehot",
                OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=100),
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
        [
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


def build_hgb_model() -> Pipeline:
    numeric_transformer = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "ordinal",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                    encoded_missing_value=-1,
                ),
            ),
        ]
    )
    preprocessor = ColumnTransformer(
        [
            ("numeric", numeric_transformer, NUMERIC_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "classifier",
                GradientBoostingClassifier(
                    max_depth=6,
                    learning_rate=0.05,
                    n_estimators=200,
                    min_samples_leaf=200,
                    random_state=42,
                ),
            ),
        ]
    )


def build_xgboost_model() -> Pipeline:
    if XGBClassifier is None:
        raise ImportError("xgboost is not installed")

    numeric_transformer = Pipeline([("imputer", SimpleImputer(strategy="median"))])
    categorical_transformer = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "ordinal",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                    encoded_missing_value=-1,
                ),
            ),
        ]
    )
    preprocessor = ColumnTransformer(
        [
            ("numeric", numeric_transformer, NUMERIC_FEATURES),
            ("categorical", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )
    return Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "classifier",
                XGBClassifier(
                    n_estimators=300,
                    max_depth=6,
                    learning_rate=0.05,
                    subsample=0.9,
                    colsample_bytree=0.8,
                    objective="binary:logistic",
                    eval_metric="logloss",
                    n_jobs=1,
                    random_state=42,
                ),
            ),
        ]
    )


def evaluate_binary_model(y_true: pd.Series, y_pred: np.ndarray, y_prob: np.ndarray) -> dict:
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
            y_true, y_pred, output_dict=True, zero_division=0
        ),
    }


def fit_probability_calibrator(
    y_true: pd.Series, probabilities: np.ndarray
) -> tuple[str, object | None, list[dict]]:
    validation_rows = []

    raw_brier = float(brier_score_loss(y_true, probabilities))
    validation_rows.append(
        {
            "method": "raw",
            "validation_brier_score": round(raw_brier, 4),
        }
    )

    sigmoid_model = LogisticRegression(max_iter=1000)
    sigmoid_model.fit(probabilities.reshape(-1, 1), y_true)
    sigmoid_probabilities = sigmoid_model.predict_proba(probabilities.reshape(-1, 1))[:, 1]
    sigmoid_brier = float(brier_score_loss(y_true, sigmoid_probabilities))
    validation_rows.append(
        {
            "method": "sigmoid",
            "validation_brier_score": round(sigmoid_brier, 4),
        }
    )

    isotonic_model = IsotonicRegression(out_of_bounds="clip")
    isotonic_model.fit(probabilities, y_true)
    isotonic_probabilities = isotonic_model.transform(probabilities)
    isotonic_brier = float(brier_score_loss(y_true, isotonic_probabilities))
    validation_rows.append(
        {
            "method": "isotonic",
            "validation_brier_score": round(isotonic_brier, 4),
        }
    )

    best_method = min(validation_rows, key=lambda row: row["validation_brier_score"])["method"]
    if best_method == "raw":
        return best_method, None, validation_rows
    if best_method == "sigmoid":
        return best_method, sigmoid_model, validation_rows
    return best_method, isotonic_model, validation_rows


def apply_probability_calibrator(
    method: str, calibrator: object | None, probabilities: np.ndarray
) -> np.ndarray:
    if method == "raw" or calibrator is None:
        return probabilities
    if method == "sigmoid":
        return calibrator.predict_proba(probabilities.reshape(-1, 1))[:, 1]
    if method == "isotonic":
        return calibrator.transform(probabilities)
    raise ValueError(f"Unknown calibration method: {method}")


def select_threshold(y_true: pd.Series, probabilities: np.ndarray) -> tuple[float, dict]:
    candidate_thresholds = np.arange(0.02, 0.51, 0.01)
    best_threshold = 0.5
    best_metrics = {"f1": -1.0}
    for threshold in candidate_thresholds:
        preds = (probabilities >= threshold).astype(int)
        metrics = {
            "threshold": round(float(threshold), 4),
            "precision": float(precision_score(y_true, preds, zero_division=0)),
            "recall": float(recall_score(y_true, preds, zero_division=0)),
            "f1": float(f1_score(y_true, preds, zero_division=0)),
        }
        if metrics["f1"] > best_metrics["f1"]:
            best_threshold = float(threshold)
            best_metrics = metrics
    best_metrics = {key: round(float(value), 4) for key, value in best_metrics.items()}
    return best_threshold, best_metrics


def save_pr_curve(y_true: pd.Series, probabilities: np.ndarray, output_path: Path):
    precision, recall, thresholds = precision_recall_curve(y_true, probabilities)
    threshold_values = list(thresholds) + [1.0]
    frame = pd.DataFrame(
        {
            "precision": precision,
            "recall": recall,
            "threshold": threshold_values,
        }
    )
    frame.to_csv(output_path, index=False)


def build_calibration_bins(y_true: pd.Series, probabilities: np.ndarray) -> list[dict]:
    prob_true, prob_pred = calibration_curve(y_true, probabilities, n_bins=10, strategy="quantile")
    return [
        {
            "avg_predicted_probability": round(float(pred), 4),
            "observed_positive_rate": round(float(true), 4),
        }
        for pred, true in zip(prob_pred, prob_true)
    ]


def build_slice_analysis(
    frame: pd.DataFrame,
    y_true: pd.Series,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
) -> dict:
    output = {}
    analysis_frame = frame.copy()
    analysis_frame["y_true"] = y_true.to_numpy()
    analysis_frame["y_pred"] = y_pred
    analysis_frame["y_prob"] = y_prob

    for column in SLICE_COLUMNS:
        working = analysis_frame.copy()
        working[column] = working[column].fillna("unknown").astype(str)
        top_values = working[column].value_counts().head(10).index.tolist()
        slices = []
        for value in top_values:
            subset = working[working[column] == value]
            slices.append(
                {
                    "slice": value,
                    "rows": int(len(subset)),
                    "positive_rate": round(float(subset["y_true"].mean()), 4),
                    "precision": round(
                        float(precision_score(subset["y_true"], subset["y_pred"], zero_division=0)),
                        4,
                    ),
                    "recall": round(
                        float(recall_score(subset["y_true"], subset["y_pred"], zero_division=0)),
                        4,
                    ),
                    "avg_predicted_probability": round(float(subset["y_prob"].mean()), 4),
                }
            )
        output[column] = slices

    year_frame = analysis_frame.copy()
    year_frame["founded_year_bucket"] = pd.cut(
        year_frame[TIME_COLUMN],
        bins=[1900, 2000, 2005, 2008, 2010, 2012],
        labels=["<=2000", "2001-2005", "2006-2008", "2009-2010", "2011-2012"],
        include_lowest=True,
    ).astype(str)
    output["founded_year_bucket"] = []
    for value, subset in year_frame.groupby("founded_year_bucket"):
        if subset.empty:
            continue
        output["founded_year_bucket"].append(
            {
                "slice": value,
                "rows": int(len(subset)),
                "positive_rate": round(float(subset["y_true"].mean()), 4),
                "precision": round(
                    float(precision_score(subset["y_true"], subset["y_pred"], zero_division=0)),
                    4,
                ),
                "recall": round(
                    float(recall_score(subset["y_true"], subset["y_pred"], zero_division=0)),
                    4,
                ),
                "avg_predicted_probability": round(float(subset["y_prob"].mean()), 4),
            }
        )
    return output


def extract_logistic_coefficients(model: Pipeline, limit: int = 15) -> dict:
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


def train_and_evaluate_model(
    model_name: str,
    model: Pipeline,
    train_core: pd.DataFrame,
    validation_frame: pd.DataFrame,
    full_train: pd.DataFrame,
    test_frame: pd.DataFrame,
    target_column: str,
    task_name: str,
) -> dict:
    feature_columns = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    if model_name == "logistic_text":
        feature_columns = feature_columns + [TEXT_FEATURE]

    x_train_core = train_core[feature_columns]
    y_train_core = train_core[target_column]
    x_validation = validation_frame[feature_columns]
    y_validation = validation_frame[target_column]
    x_full_train = full_train[feature_columns]
    y_full_train = full_train[target_column]
    x_test = test_frame[feature_columns]
    y_test = test_frame[target_column]

    model.fit(x_train_core, y_train_core)
    validation_prob_raw = model.predict_proba(x_validation)[:, 1]
    calibration_method, calibrator, calibration_validation_scores = fit_probability_calibrator(
        y_validation, validation_prob_raw
    )
    validation_prob = apply_probability_calibrator(
        calibration_method, calibrator, validation_prob_raw
    )
    threshold, threshold_metrics = select_threshold(y_validation, validation_prob)

    model.fit(x_full_train, y_full_train)
    test_prob_raw = model.predict_proba(x_test)[:, 1]
    test_prob = apply_probability_calibrator(calibration_method, calibrator, test_prob_raw)
    test_pred = (test_prob >= threshold).astype(int)

    model_dir = ARTIFACT_DIR / task_name / model_name
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "model.joblib"
    metrics_path = model_dir / "metrics.json"
    pr_curve_path = model_dir / "pr_curve.csv"
    predictions_path = model_dir / "holdout_predictions.csv"
    slice_path = model_dir / "slice_analysis.json"

    predictions = test_frame[["org_id", "name", "founded_year", "category", target_column]].copy()
    predictions["predicted_probability"] = test_prob
    predictions["predicted_label"] = test_pred
    predictions.to_csv(predictions_path, index=False)
    save_pr_curve(y_test, test_prob, pr_curve_path)

    metrics = {
        "model_name": model_name,
        "task": task_name,
        "target_column": target_column,
        "threshold_selection": threshold_metrics,
        "selected_threshold": round(float(threshold), 4),
        "calibration_method": calibration_method,
        "calibration_validation_scores": calibration_validation_scores,
        "train_rows": int(len(full_train)),
        "validation_rows": int(len(validation_frame)),
        "test_rows": int(len(test_frame)),
        "metrics": evaluate_binary_model(y_test, test_pred, test_prob),
        "calibration_bins": build_calibration_bins(y_test, test_prob),
    }
    if model_name == "logistic_text":
        metrics.update(extract_logistic_coefficients(model))

    slice_analysis = build_slice_analysis(test_frame, y_test, test_pred, test_prob)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    slice_path.write_text(json.dumps(slice_analysis, indent=2), encoding="utf-8")
    joblib.dump({"model": model, "threshold": threshold, "task": task_name}, model_path)

    return {
        "model_name": model_name,
        "selected_threshold": metrics["selected_threshold"],
        "metrics": metrics["metrics"],
        "artifacts": {
            "model": str(model_path),
            "metrics": str(metrics_path),
            "pr_curve": str(pr_curve_path),
            "predictions": str(predictions_path),
            "slice_analysis": str(slice_path),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Train temporal benchmark models for startup outcome prediction."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Path to the processed startup feature table.",
    )
    parser.add_argument(
        "--task",
        choices=sorted(TARGET_OPTIONS.keys()) + ["all"],
        default="all",
        help="Outcome task to train.",
    )
    args = parser.parse_args()

    dataset = load_dataset(args.input)
    task_names = sorted(TARGET_OPTIONS.keys()) if args.task == "all" else [args.task]
    summary = {}

    for task_name in task_names:
        target_column = TARGET_OPTIONS[task_name]
        frame = filter_modeling_frame(dataset, target_column)
        train_frame, test_frame, split_year = build_temporal_split(frame, min_rows=5000)
        train_core, validation_frame = build_train_validation_split(train_frame, target_column)

        results = []
        results.append(
            train_and_evaluate_model(
                "logistic_text",
                build_logistic_model(),
                train_core,
                validation_frame,
                train_frame,
                test_frame,
                target_column,
                task_name,
            )
        )
        results.append(
            train_and_evaluate_model(
                "hist_gradient_boosting",
                build_hgb_model(),
                train_core,
                validation_frame,
                train_frame,
                test_frame,
                target_column,
                task_name,
            )
        )
        if XGBClassifier is not None:
            results.append(
                train_and_evaluate_model(
                    "xgboost",
                    build_xgboost_model(),
                    train_core,
                    validation_frame,
                    train_frame,
                    test_frame,
                    target_column,
                    task_name,
                )
            )

        summary[task_name] = {
            "target_column": target_column,
            "temporal_split_year": int(split_year),
            "train_year_range": [
                int(train_frame[TIME_COLUMN].min()),
                int(train_frame[TIME_COLUMN].max()),
            ],
            "test_year_range": [
                int(test_frame[TIME_COLUMN].min()),
                int(test_frame[TIME_COLUMN].max()),
            ],
            "models": results,
        }

    summary_path = ARTIFACT_DIR / "benchmark_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Saved benchmark summary to {summary_path}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
