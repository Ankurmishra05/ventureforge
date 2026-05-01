# Raw Dataset Placement

Place the Kaggle `Startup Investments` CSV files in this directory.

Expected files:

- `organizations.csv` (required)
- `funding_rounds.csv` (recommended)
- `investments.csv` (recommended)
- `acquisitions.csv` (recommended)
- `ipos.csv` (recommended)

Source dataset:

- Kaggle `Startup Investments`: https://www.kaggle.com/datasets/justinas/startup-investments

Then run:

```bash
python backend/scripts/prepare_startup_dataset.py
```
