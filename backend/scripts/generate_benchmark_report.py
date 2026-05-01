import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SUMMARY_PATH = REPO_ROOT / "backend" / "model_artifacts" / "benchmark_summary.json"
OUTPUT_PATH = REPO_ROOT / "docs" / "model-benchmark-report.md"


def load_summary() -> dict:
    if not SUMMARY_PATH.exists():
        raise FileNotFoundError(
            f"Benchmark summary not found: {SUMMARY_PATH}. Run train_outcome_benchmarks.py first."
        )
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


def format_model_section(model: dict) -> list[str]:
    metrics = model["metrics"]
    lines = [
        f"### {model['model_name']}",
        "",
        f"- Selected threshold: `{model['selected_threshold']}`",
        f"- ROC-AUC: `{metrics['roc_auc']}`",
        f"- PR-AUC: `{metrics['pr_auc']}`",
        f"- Brier score: `{metrics['brier_score']}`",
        f"- Precision: `{metrics['precision']}`",
        f"- Recall: `{metrics['recall']}`",
        f"- F1: `{metrics['f1']}`",
        f"- Predicted positive rate: `{metrics['predicted_positive_rate']}`",
    ]
    return lines


def choose_best_model(models: list[dict]) -> dict:
    return max(models, key=lambda item: item["metrics"]["pr_auc"])


def build_report(summary: dict) -> str:
    lines = [
        "# VentureForge Benchmark Report",
        "",
        "This report summarizes temporal holdout benchmark results on the Kaggle `Startup Investments` dataset after the first 730-day early-stage snapshot feature build.",
        "",
    ]

    for task_name, task_data in summary.items():
        best_model = choose_best_model(task_data["models"])
        lines.extend(
            [
                f"## Task: {task_name}",
                "",
                f"- Target column: `{task_data['target_column']}`",
                f"- Temporal split year: `{task_data['temporal_split_year']}`",
                f"- Train years: `{task_data['train_year_range'][0]}-{task_data['train_year_range'][1]}`",
                f"- Test years: `{task_data['test_year_range'][0]}-{task_data['test_year_range'][1]}`",
                f"- Best model by PR-AUC: `{best_model['model_name']}` with `{best_model['metrics']['pr_auc']}`",
                "",
            ]
        )
        for model in task_data["models"]:
            lines.extend(format_model_section(model))
            lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "- `future_funding` is currently the stronger supervised task and produces materially better PR-AUC than `exit`.",
            "- Gradient boosting performs better than the linear text baseline on both tasks in the current temporal holdout.",
            "- The tasks are imbalanced, so PR-AUC, recall, precision, and calibration are more useful than accuracy.",
            "- These results should be treated as a baseline for iterative feature engineering, calibration, and model comparison.",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    summary = load_summary()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_report(summary), encoding="utf-8")
    print(f"Saved benchmark report to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
