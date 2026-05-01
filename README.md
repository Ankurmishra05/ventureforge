# VentureForge

VentureForge is a hybrid `GenAI + ML` startup intelligence platform. It combines a multi-agent LLM workflow for startup brief generation with supervised ML models trained on real Crunchbase-style startup event data for `future funding` and `exit` prediction.

## What It Does

- Generates startup research, branding, finance, and decision outputs through a multi-step LLM workflow
- Trains temporal startup outcome models on real multi-table startup data
- Serves authenticated prediction APIs for startup scoring
- Exposes both the GenAI workflow and the ML scoring flow through a Next.js dashboard

## Project Angles

This project is strongest when positioned as:

- a `hybrid GenAI + predictive ML system`
- a `multi-agent LLM application with model-based decision support`
- a `full-stack ML product` with data engineering, benchmarking, and API serving

## Architecture

### Backend

- `FastAPI` for authenticated API routes
- `SQLAlchemy` + `Alembic` for persistence
- `JWT` auth for protected routes
- `Groq`, `OpenRouter`, and `Ollama` support for LLM provider orchestration

### GenAI / Agentic Workflow

The startup brief pipeline orchestrates:

- `research agent`
- `branding agent`
- `finance agent`
- `decision agent`

These run through a shared orchestration flow and return structured outputs through the API.

### ML / DS Pipeline

The ML side is built on the Kaggle `Startup Investments` dataset and includes:

- multi-table ingestion from raw Crunchbase-style CSVs
- company-level feature generation
- early-stage snapshot features from the first `730` days after founding
- temporal train/validation/test evaluation
- threshold tuning
- probability calibration
- slice-based error analysis

## Dataset

Source dataset:

- Kaggle `Startup Investments`: https://www.kaggle.com/datasets/justinas/startup-investments

Raw CSVs should be placed in:

- `data/raw/startup-investments/`

Expected important files:

- `objects.csv`
- `funding_rounds.csv`
- `investments.csv`
- `acquisitions.csv`
- `ipos.csv`

Raw CSVs are intentionally ignored from Git.

## Core Prediction Tasks

- `future_funding`: whether a startup raises funding after the first 730 days
- `exit`: whether a startup eventually reaches acquisition or IPO

## Best Current Benchmark

Best current model:

- `XGBoost` on the `future_funding` task

Current temporal holdout metrics:

- ROC-AUC: `0.848`
- PR-AUC: `0.3211`
- Precision: `0.2705`
- Recall: `0.5016`
- F1: `0.3514`
- Decision threshold: `0.27`

This model is also wired into the backend prediction endpoint.

## Important Files

### Data and Training

- [backend/scripts/prepare_startup_dataset.py](backend/scripts/prepare_startup_dataset.py)
- [backend/scripts/train_outcome_benchmarks.py](backend/scripts/train_outcome_benchmarks.py)
- [backend/scripts/generate_benchmark_report.py](backend/scripts/generate_benchmark_report.py)
- [backend/scripts/generate_portfolio_writeup.py](backend/scripts/generate_portfolio_writeup.py)

### Model Serving

- [backend/app/services/outcome_model.py](backend/app/services/outcome_model.py)
- [backend/app/api/routes/predictions.py](backend/app/api/routes/predictions.py)

### Reports

- [docs/model-benchmark-report.md](docs/model-benchmark-report.md)
- [docs/portfolio-case-study.md](docs/portfolio-case-study.md)

## How To Run

### Backend

From `backend/`:

```bash
python -m uvicorn app.main:app --reload
```

### Frontend

From `frontend/`:

```bash
npm install
npm run dev
```

### Build the Dataset

```bash
python backend/scripts/prepare_startup_dataset.py
```

### Run Benchmarks

```bash
python backend/scripts/train_outcome_benchmarks.py --task all
python backend/scripts/generate_benchmark_report.py
python backend/scripts/generate_portfolio_writeup.py
```

## API Endpoints

### Generate startup brief

- `POST /generate-startup`

### Predict future funding

- `POST /predictions/future-funding`

Example payload:

```json
{
  "founded_year": 2010,
  "category": "enterprise",
  "country": "USA",
  "state": "CA",
  "city": "San Francisco",
  "description": "Workflow automation software for mid-market finance teams",
  "early_latest_round_type": "series_a",
  "early_num_funding_rounds": 2,
  "early_total_raised_usd": 3500000,
  "early_avg_raised_usd": 1750000,
  "early_max_raised_usd": 2500000,
  "early_avg_participants": 3,
  "early_max_participants": 4
}
```

## Smoke Test Status

Verified locally in this workspace:

- backend startup succeeded
- auth registration succeeded
- protected prediction endpoint returned valid results
- frontend lint passed
- frontend TypeScript check passed

Next.js `build` and `dev` process startup were blocked in this environment by Windows sandbox `spawn EPERM`, so browser-level verification was partially environment-limited rather than code-limited.

## CV Positioning

Good positioning:

- `Hybrid GenAI + ML startup intelligence platform`
- `Multi-agent LLM workflow with calibrated startup outcome prediction`
- `Full-stack ML product with temporal benchmarking and model serving`

Avoid overstating it as:

- fully autonomous agent system
- production-grade AGI agent
- state-of-the-art startup prediction engine
