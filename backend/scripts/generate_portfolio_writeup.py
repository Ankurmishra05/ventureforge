import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SUMMARY_PATH = REPO_ROOT / "backend" / "model_artifacts" / "benchmark_summary.json"
OUTPUT_PATH = REPO_ROOT / "docs" / "portfolio-case-study.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_summary() -> dict:
    if not SUMMARY_PATH.exists():
        raise FileNotFoundError(
            f"Benchmark summary not found: {SUMMARY_PATH}. Run train_outcome_benchmarks.py first."
        )
    return load_json(SUMMARY_PATH)


def pick_best_model(task_data: dict) -> dict:
    return max(task_data["models"], key=lambda model: model["metrics"]["pr_auc"])


def build_case_study(summary: dict) -> str:
    future_best = pick_best_model(summary["future_funding"])
    exit_best = pick_best_model(summary["exit"])

    future_metrics_path = Path(future_best["artifacts"]["metrics"])
    future_slice_path = Path(future_best["artifacts"]["slice_analysis"])
    future_metrics = load_json(future_metrics_path)
    future_slices = load_json(future_slice_path)

    top_category_slices = future_slices.get("category", [])[:5]
    calibration_rows = future_metrics.get("calibration_bins", [])[-3:]

    lines = [
        "# VentureForge Portfolio Case Study",
        "",
        "## Problem",
        "",
        "The goal was to move VentureForge from a prompt-based startup idea app into a defensible machine learning project with real data, temporal validation, calibrated probabilities, and measurable business-style prediction tasks.",
        "",
        "## Dataset",
        "",
        "- Source: Kaggle `Startup Investments` dataset based on a Crunchbase snapshot",
        "- Unit of analysis: company",
        "- Raw structure: multi-table startup event data including organizations, funding rounds, acquisitions, IPOs, and investments",
        "- Processed feature table: `data/processed/startup_company_features.csv`",
        "- Early-stage snapshot: first 730 days after founding",
        "",
        "## Prediction Tasks",
        "",
        "- `future_funding`: whether a startup receives funding after the early-stage snapshot window",
        "- `exit`: whether a startup eventually reaches acquisition or IPO",
        "",
        "## Modeling Approach",
        "",
        "- Temporal train/test split using `founded_year`",
        "- Validation-era threshold tuning instead of a fixed 0.5 threshold",
        "- Post-hoc probability calibration comparison across raw, sigmoid, and isotonic methods",
        "- Benchmarks: text-aware logistic regression, gradient boosting, and XGBoost",
        "",
        "## Best Results",
        "",
        f"- Best `future_funding` model: `{future_best['model_name']}`",
        f"- ROC-AUC: `{future_best['metrics']['roc_auc']}`",
        f"- PR-AUC: `{future_best['metrics']['pr_auc']}`",
        f"- Precision: `{future_best['metrics']['precision']}`",
        f"- Recall: `{future_best['metrics']['recall']}`",
        f"- F1: `{future_best['metrics']['f1']}`",
        f"- Threshold: `{future_best['selected_threshold']}`",
        "",
        f"- Best `exit` model: `{exit_best['model_name']}` with PR-AUC `{exit_best['metrics']['pr_auc']}`",
        "",
        "## Calibration Findings",
        "",
        f"- Selected calibration method for the best future-funding model: `{future_metrics['calibration_method']}`",
        "- Validation Brier scores:",
    ]

    for row in future_metrics["calibration_validation_scores"]:
        lines.append(
            f"- `{row['method']}`: `{row['validation_brier_score']}`"
        )

    lines.extend(
        [
            "",
            "Top holdout calibration bins from the best future-funding model:",
        ]
    )

    for row in calibration_rows:
        lines.append(
            f"- predicted `{row['avg_predicted_probability']}`, observed `{row['observed_positive_rate']}`"
        )

    lines.extend(
        [
            "",
            "## Slice Analysis",
            "",
            "Example category slices from the best future-funding model:",
        ]
    )

    for row in top_category_slices:
        lines.append(
            f"- `{row['slice']}`: rows `{row['rows']}`, positive rate `{row['positive_rate']}`, precision `{row['precision']}`, recall `{row['recall']}`"
        )

    lines.extend(
        [
            "",
            "## What This Demonstrates",
            "",
            "- Real multi-table feature engineering from messy startup event data",
            "- Point-in-time target construction with leakage-aware evaluation",
            "- Benchmark comparison across linear and tree-based models",
            "- Threshold tuning and probability calibration for imbalanced classification",
            "- Slice-based performance analysis instead of relying on a single accuracy number",
            "",
            "## Next Steps",
            "",
            "- Add SHAP-based local explanations for the serving model",
            "- Train on richer text features such as sentence embeddings",
            "- Connect predictions and explanations to the product UI",
        ]
    )

    return "\n".join(lines)


def main():
    summary = load_summary()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_case_study(summary), encoding="utf-8")
    print(f"Saved portfolio writeup to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
