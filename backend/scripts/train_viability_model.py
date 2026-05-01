import json
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = REPO_ROOT / "data" / "startup_benchmark.jsonl"
ARTIFACT_DIR = REPO_ROOT / "backend" / "model_artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "startup_viability.joblib"
METRICS_PATH = ARTIFACT_DIR / "startup_viability_metrics.json"


def load_dataset(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def build_text(row: dict) -> str:
    return f'{row["idea"].strip()} [AUDIENCE] {row["audience"].strip()}'


def main():
    rows = load_dataset(DATASET_PATH)
    if len(rows) < 12:
        raise ValueError("Dataset is too small for a meaningful train/test split.")

    texts = [build_text(row) for row in rows]
    verdicts = [row["verdict"].upper() for row in rows]
    risk_scores = [float(row["risk_score"]) for row in rows]

    (
        x_train,
        x_test,
        y_train,
        y_test,
        risk_train,
        risk_test,
    ) = train_test_split(
        texts,
        verdicts,
        risk_scores,
        test_size=0.25,
        random_state=42,
        stratify=verdicts,
    )

    classifier = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    classifier.fit(x_train, y_train)

    risk_regressor = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ("reg", Ridge(alpha=1.0)),
        ]
    )
    risk_regressor.fit(x_train, risk_train)

    predicted_verdicts = classifier.predict(x_test)
    predicted_risk_scores = risk_regressor.predict(x_test)

    metrics = {
        "dataset_path": str(DATASET_PATH),
        "sample_count": len(rows),
        "train_count": len(x_train),
        "test_count": len(x_test),
        "accuracy": round(float(accuracy_score(y_test, predicted_verdicts)), 4),
        "risk_mae": round(float(mean_absolute_error(risk_test, predicted_risk_scores)), 4),
        "classification_report": classification_report(
            y_test,
            predicted_verdicts,
            output_dict=True,
            zero_division=0,
        ),
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "classifier": classifier,
            "risk_regressor": risk_regressor,
            "labels": list(classifier.classes_),
            "sample_count": len(rows),
            "model_version": "startup-viability-baseline-v1",
        },
        ARTIFACT_PATH,
    )
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print("Saved artifact:", ARTIFACT_PATH)
    print("Saved metrics:", METRICS_PATH)
    print("Accuracy:", metrics["accuracy"])
    print("Risk MAE:", metrics["risk_mae"])


if __name__ == "__main__":
    main()
