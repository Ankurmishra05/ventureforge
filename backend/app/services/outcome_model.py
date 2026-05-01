from pathlib import Path

import joblib
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = (
    REPO_ROOT
    / "model_artifacts"
    / "future_funding"
    / "xgboost"
    / "model.joblib"
)

MODEL_FEATURES = [
    "founded_year",
    "description_length",
    "early_num_funding_rounds",
    "early_total_raised_usd",
    "early_avg_raised_usd",
    "early_max_raised_usd",
    "early_avg_participants",
    "early_max_participants",
    "category",
    "country",
    "state",
    "city",
    "early_latest_round_type",
]

NEUTRAL_VALUES = {
    "founded_year": 2008,
    "description_length": 0,
    "early_num_funding_rounds": 0,
    "early_total_raised_usd": 0,
    "early_avg_raised_usd": 0,
    "early_max_raised_usd": 0,
    "early_avg_participants": 0,
    "early_max_participants": 0,
    "category": "other",
    "country": "unknown",
    "state": "unknown",
    "city": "unknown",
    "early_latest_round_type": "unknown",
}


def load_future_funding_model(model_path: Path = DEFAULT_MODEL_PATH):
    if not model_path.exists():
        return None
    return joblib.load(model_path)


def predict_future_funding(payload: dict) -> dict:
    artifact = load_future_funding_model()
    if artifact is None:
        raise FileNotFoundError(
            f"Future funding model artifact not found at {DEFAULT_MODEL_PATH}."
        )

    model = artifact["model"]
    threshold = float(artifact["threshold"])
    description = str(payload.get("description", "") or "")

    row = {
        "founded_year": payload.get("founded_year"),
        "description_length": len(description),
        "early_num_funding_rounds": payload.get("early_num_funding_rounds", 0),
        "early_total_raised_usd": payload.get("early_total_raised_usd", 0),
        "early_avg_raised_usd": payload.get("early_avg_raised_usd", 0),
        "early_max_raised_usd": payload.get("early_max_raised_usd", 0),
        "early_avg_participants": payload.get("early_avg_participants", 0),
        "early_max_participants": payload.get("early_max_participants", 0),
        "category": payload.get("category"),
        "country": payload.get("country"),
        "state": payload.get("state"),
        "city": payload.get("city"),
        "early_latest_round_type": payload.get("early_latest_round_type"),
    }

    frame = pd.DataFrame([row], columns=MODEL_FEATURES)
    probability = float(model.predict_proba(frame)[0, 1])
    predicted_label = int(probability >= threshold)
    explanation = build_prediction_explanation(model, row, probability)

    return {
        "predicted_probability": round(probability, 4),
        "predicted_label": predicted_label,
        "selected_threshold": round(threshold, 4),
        "model_version": "future-funding-xgboost-v1",
        "task": artifact.get("task", "future_funding"),
        "features_used": row,
        "explanation": explanation,
    }


def build_prediction_explanation(model, row: dict, probability: float) -> list[dict]:
    items = []
    for feature in MODEL_FEATURES:
        perturbed = dict(row)
        perturbed[feature] = NEUTRAL_VALUES[feature]
        perturbed_frame = pd.DataFrame([perturbed], columns=MODEL_FEATURES)
        perturbed_probability = float(model.predict_proba(perturbed_frame)[0, 1])
        delta = probability - perturbed_probability
        if abs(delta) < 0.005:
            continue
        direction = "increases" if delta > 0 else "decreases"
        items.append(
            {
                "feature": feature,
                "value": row[feature],
                "direction": direction,
                "impact": round(abs(delta), 4),
            }
        )

    items.sort(key=lambda item: item["impact"], reverse=True)
    return items[:5]
