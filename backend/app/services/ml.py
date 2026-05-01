import json
from pathlib import Path

import joblib

MODEL_ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2] / "model_artifacts" / "startup_viability.joblib"
)


def load_viability_model():
    if not MODEL_ARTIFACT_PATH.exists():
        return None

    return joblib.load(MODEL_ARTIFACT_PATH)


def predict_startup_signal(idea: str, audience: str) -> dict | None:
    artifact = load_viability_model()
    if artifact is None:
        return None

    model = artifact["classifier"]
    risk_model = artifact["risk_regressor"]
    labels = artifact["labels"]
    model_version = artifact["model_version"]
    sample_count = artifact["sample_count"]

    text = f"{idea.strip()} [AUDIENCE] {audience.strip()}"
    probabilities = model.predict_proba([text])[0]
    label_probabilities = {
        label.lower(): round(float(probability), 4)
        for label, probability in zip(labels, probabilities)
    }
    predicted_verdict = str(model.predict([text])[0]).upper()
    predicted_risk_score = float(risk_model.predict([text])[0])
    predicted_risk_score = max(0.0, min(100.0, round(predicted_risk_score, 2)))

    return {
        "predicted_verdict": predicted_verdict,
        "predicted_risk_score": predicted_risk_score,
        "build_probability": label_probabilities.get("build", 0.0),
        "pivot_probability": label_probabilities.get("pivot", 0.0),
        "avoid_probability": label_probabilities.get("avoid", 0.0),
        "model_version": model_version,
        "training_sample_count": sample_count,
    }


def save_metrics(metrics: dict):
    metrics_path = MODEL_ARTIFACT_PATH.with_name("startup_viability_metrics.json")
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
