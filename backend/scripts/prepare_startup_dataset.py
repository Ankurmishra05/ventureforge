import argparse
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW_DIR = REPO_ROOT / "data" / "raw" / "startup-investments"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "data" / "processed" / "startup_company_features.csv"
EARLY_SIGNAL_WINDOW_DAYS = 730
REFERENCE_DATE = pd.Timestamp("2013-12-31")


def snake_case_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
        for column in frame.columns
    ]
    return frame


def read_csv_if_exists(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return snake_case_columns(pd.read_csv(path, low_memory=False))


def first_available(frame: pd.DataFrame, candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in frame.columns:
            return candidate
    return None


def ensure_datetime(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        if column in frame.columns:
            frame[column] = pd.to_datetime(frame[column], errors="coerce")
    return frame


def load_required_tables(raw_dir: Path) -> dict[str, pd.DataFrame | None]:
    tables = {
        "organizations": read_csv_if_exists(raw_dir / "organizations.csv"),
        "objects": read_csv_if_exists(raw_dir / "objects.csv"),
        "funding_rounds": read_csv_if_exists(raw_dir / "funding_rounds.csv"),
        "acquisitions": read_csv_if_exists(raw_dir / "acquisitions.csv"),
        "ipos": read_csv_if_exists(raw_dir / "ipos.csv"),
        "investments": read_csv_if_exists(raw_dir / "investments.csv"),
    }

    if tables["organizations"] is None:
        tables["organizations"] = tables["objects"]

    if tables["organizations"] is None:
        raise FileNotFoundError(
            f"Missing required file: {raw_dir / 'organizations.csv'} or {raw_dir / 'objects.csv'}"
        )

    return tables


def build_base_organizations(organizations: pd.DataFrame) -> pd.DataFrame:
    organizations = ensure_datetime(
        organizations,
        ["founded_at", "closed_at", "first_funding_at", "last_funding_at"],
    )

    entity_type_column = first_available(organizations, ["entity_type"])
    if entity_type_column:
        organizations = organizations[
            organizations[entity_type_column].astype(str).str.lower() == "company"
        ].copy()

    id_column = first_available(organizations, ["object_id", "id", "permalink"])
    if id_column is None:
        raise ValueError("organizations.csv must contain object_id, id, or permalink.")

    name_column = first_available(organizations, ["name"])
    category_column = first_available(
        organizations, ["category_code", "category_list", "market"]
    )
    country_column = first_available(organizations, ["country_code", "country"])
    state_column = first_available(organizations, ["state_code", "state"])
    city_column = first_available(organizations, ["city"])
    founded_column = first_available(organizations, ["founded_at"])
    founded_year_column = first_available(organizations, ["founded_year"])
    description_column = first_available(
        organizations,
        ["short_description", "description", "overview", "tagline"],
    )
    status_column = first_available(organizations, ["status"])
    funding_total_column = first_available(
        organizations,
        [
            "funding_total_usd",
            "funding_total",
            "total_funding_usd",
            "raised_amount_usd",
        ],
    )

    base = pd.DataFrame(
        {
            "org_id": organizations[id_column].astype(str),
            "name": organizations[name_column] if name_column else "",
            "category": organizations[category_column] if category_column else pd.NA,
            "country": organizations[country_column] if country_column else pd.NA,
            "state": organizations[state_column] if state_column else pd.NA,
            "city": organizations[city_column] if city_column else pd.NA,
            "founded_at": organizations[founded_column] if founded_column else pd.NaT,
            "founded_year": organizations[founded_year_column]
            if founded_year_column
            else pd.NA,
            "description": organizations[description_column]
            if description_column
            else pd.NA,
            "status": organizations[status_column] if status_column else pd.NA,
            "funding_total_usd_org": pd.to_numeric(
                organizations[funding_total_column], errors="coerce"
            )
            if funding_total_column
            else pd.NA,
        }
    )

    base["founded_year"] = base["founded_year"].fillna(
        pd.to_datetime(base["founded_at"], errors="coerce").dt.year
    )
    base["description"] = base["description"].fillna("").astype(str).str.strip()
    base["name"] = base["name"].fillna("").astype(str).str.strip()
    return base.drop_duplicates(subset=["org_id"])


def aggregate_funding_rounds(funding_rounds: pd.DataFrame | None) -> pd.DataFrame:
    if funding_rounds is None or funding_rounds.empty:
        return pd.DataFrame(columns=["org_id"])

    funding_rounds = ensure_datetime(funding_rounds, ["funded_at"])
    object_column = first_available(funding_rounds, ["object_id", "company_object_id"])
    amount_column = first_available(funding_rounds, ["raised_amount_usd", "raised_amount"])
    round_type_column = first_available(
        funding_rounds, ["funding_round_type", "funding_round_code"]
    )
    participants_column = first_available(funding_rounds, ["participants"])

    if object_column is None:
        return pd.DataFrame(columns=["org_id"])

    frame = funding_rounds.copy()
    frame["org_id"] = frame[object_column].astype(str)
    frame["raised_amount_usd"] = pd.to_numeric(
        frame[amount_column], errors="coerce"
    ) if amount_column else 0
    frame["participants"] = pd.to_numeric(
        frame[participants_column], errors="coerce"
    ) if participants_column else 0

    grouped = frame.groupby("org_id", dropna=False)
    summary = grouped.agg(
        num_funding_rounds=("org_id", "size"),
        total_raised_usd_rounds=("raised_amount_usd", "sum"),
        avg_raised_usd_round=("raised_amount_usd", "mean"),
        max_raised_usd_round=("raised_amount_usd", "max"),
        avg_participants=("participants", "mean"),
        max_participants=("participants", "max"),
        first_round_at=("funded_at", "min"),
        last_round_at=("funded_at", "max"),
    ).reset_index()

    if round_type_column:
        latest_round_type = (
            frame.sort_values("funded_at")
            .dropna(subset=["org_id"])
            .groupby("org_id")[round_type_column]
            .last()
            .rename("latest_round_type")
            .reset_index()
        )
        summary = summary.merge(latest_round_type, on="org_id", how="left")

    return summary


def aggregate_early_funding_rounds(
    organizations: pd.DataFrame, funding_rounds: pd.DataFrame | None
) -> pd.DataFrame:
    if funding_rounds is None or funding_rounds.empty:
        return pd.DataFrame(columns=["org_id"])

    object_column = first_available(funding_rounds, ["object_id", "company_object_id"])
    amount_column = first_available(funding_rounds, ["raised_amount_usd", "raised_amount"])
    participants_column = first_available(funding_rounds, ["participants"])
    round_type_column = first_available(
        funding_rounds, ["funding_round_type", "funding_round_code"]
    )

    if object_column is None:
        return pd.DataFrame(columns=["org_id"])

    frame = funding_rounds.copy()
    frame = ensure_datetime(frame, ["funded_at"])
    frame["org_id"] = frame[object_column].astype(str)
    frame["raised_amount_usd"] = pd.to_numeric(
        frame[amount_column], errors="coerce"
    ) if amount_column else 0
    frame["participants"] = pd.to_numeric(
        frame[participants_column], errors="coerce"
    ) if participants_column else 0

    founded_dates = organizations[["org_id", "founded_at"]].copy()
    frame = frame.merge(founded_dates, on="org_id", how="left")
    frame["days_from_founding_to_round"] = (
        frame["funded_at"] - pd.to_datetime(frame["founded_at"], errors="coerce")
    ).dt.days
    early_frame = frame[
        frame["days_from_founding_to_round"].notna()
        & frame["days_from_founding_to_round"].ge(0)
        & frame["days_from_founding_to_round"].le(EARLY_SIGNAL_WINDOW_DAYS)
    ].copy()

    if early_frame.empty:
        return pd.DataFrame(columns=["org_id"])

    summary = (
        early_frame.groupby("org_id", dropna=False)
        .agg(
            early_num_funding_rounds=("org_id", "size"),
            early_total_raised_usd=("raised_amount_usd", "sum"),
            early_avg_raised_usd=("raised_amount_usd", "mean"),
            early_max_raised_usd=("raised_amount_usd", "max"),
            early_avg_participants=("participants", "mean"),
            early_max_participants=("participants", "max"),
            early_first_round_at=("funded_at", "min"),
            early_last_round_at=("funded_at", "max"),
        )
        .reset_index()
    )

    if round_type_column:
        latest_round_type = (
            early_frame.sort_values("funded_at")
            .groupby("org_id")[round_type_column]
            .last()
            .rename("early_latest_round_type")
            .reset_index()
        )
        summary = summary.merge(latest_round_type, on="org_id", how="left")

    return summary


def aggregate_post_early_funding_rounds(
    organizations: pd.DataFrame, funding_rounds: pd.DataFrame | None
) -> pd.DataFrame:
    if funding_rounds is None or funding_rounds.empty:
        return pd.DataFrame(columns=["org_id"])

    object_column = first_available(funding_rounds, ["object_id", "company_object_id"])
    amount_column = first_available(funding_rounds, ["raised_amount_usd", "raised_amount"])
    participants_column = first_available(funding_rounds, ["participants"])

    if object_column is None:
        return pd.DataFrame(columns=["org_id"])

    frame = funding_rounds.copy()
    frame = ensure_datetime(frame, ["funded_at"])
    frame["org_id"] = frame[object_column].astype(str)
    frame["raised_amount_usd"] = pd.to_numeric(
        frame[amount_column], errors="coerce"
    ) if amount_column else 0
    frame["participants"] = pd.to_numeric(
        frame[participants_column], errors="coerce"
    ) if participants_column else 0

    founded_dates = organizations[["org_id", "founded_at"]].copy()
    frame = frame.merge(founded_dates, on="org_id", how="left")
    frame["days_from_founding_to_round"] = (
        frame["funded_at"] - pd.to_datetime(frame["founded_at"], errors="coerce")
    ).dt.days
    post_early_frame = frame[
        frame["days_from_founding_to_round"].notna()
        & frame["days_from_founding_to_round"].gt(EARLY_SIGNAL_WINDOW_DAYS)
    ].copy()

    if post_early_frame.empty:
        return pd.DataFrame(columns=["org_id"])

    return (
        post_early_frame.groupby("org_id", dropna=False)
        .agg(
            post_early_num_funding_rounds=("org_id", "size"),
            post_early_total_raised_usd=("raised_amount_usd", "sum"),
            post_early_avg_participants=("participants", "mean"),
            post_early_first_round_at=("funded_at", "min"),
        )
        .reset_index()
    )


def aggregate_investments(investments: pd.DataFrame | None) -> pd.DataFrame:
    if investments is None or investments.empty:
        return pd.DataFrame(columns=["org_id"])

    funded_object_column = first_available(
        investments, ["funded_object_id", "company_object_id", "object_id"]
    )
    investor_object_column = first_available(
        investments, ["investor_object_id", "investor_id"]
    )

    if funded_object_column is None:
        return pd.DataFrame(columns=["org_id"])

    frame = investments.copy()
    frame["org_id"] = frame[funded_object_column].astype(str)

    summary = (
        frame.groupby("org_id", dropna=False)
        .agg(
            num_investment_rows=("org_id", "size"),
            unique_investor_count=(investor_object_column, "nunique")
            if investor_object_column
            else ("org_id", "size"),
        )
        .reset_index()
    )
    return summary


def aggregate_acquisitions(acquisitions: pd.DataFrame | None) -> pd.DataFrame:
    if acquisitions is None or acquisitions.empty:
        return pd.DataFrame(columns=["org_id"])

    acquisitions = ensure_datetime(acquisitions, ["acquired_at", "price_updated_at"])
    acquired_column = first_available(
        acquisitions,
        ["acquired_object_id", "company_object_id", "object_id"],
    )
    price_column = first_available(acquisitions, ["price_amount", "price_amount_usd"])

    if acquired_column is None:
        return pd.DataFrame(columns=["org_id"])

    frame = acquisitions.copy()
    frame["org_id"] = frame[acquired_column].astype(str)
    frame["acquisition_price_usd"] = pd.to_numeric(
        frame[price_column], errors="coerce"
    ) if price_column else pd.NA

    summary = (
        frame.groupby("org_id", dropna=False)
        .agg(
            acquisition_count=("org_id", "size"),
            first_acquired_at=("acquired_at", "min"),
            last_acquired_at=("acquired_at", "max"),
            max_acquisition_price_usd=("acquisition_price_usd", "max"),
        )
        .reset_index()
    )
    return summary


def aggregate_ipos(ipos: pd.DataFrame | None) -> pd.DataFrame:
    if ipos is None or ipos.empty:
        return pd.DataFrame(columns=["org_id"])

    ipos = ensure_datetime(ipos, ["public_at"])
    object_column = first_available(ipos, ["object_id", "company_object_id"])
    valuation_column = first_available(ipos, ["valuation_amount", "valuation_amount_usd"])
    raised_column = first_available(ipos, ["raised_amount", "raised_amount_usd"])

    if object_column is None:
        return pd.DataFrame(columns=["org_id"])

    frame = ipos.copy()
    frame["org_id"] = frame[object_column].astype(str)
    frame["ipo_valuation_amount"] = pd.to_numeric(
        frame[valuation_column], errors="coerce"
    ) if valuation_column else pd.NA
    frame["ipo_raised_amount"] = pd.to_numeric(
        frame[raised_column], errors="coerce"
    ) if raised_column else pd.NA

    summary = (
        frame.groupby("org_id", dropna=False)
        .agg(
            ipo_count=("org_id", "size"),
            first_public_at=("public_at", "min"),
            last_public_at=("public_at", "max"),
            max_ipo_valuation=("ipo_valuation_amount", "max"),
            max_ipo_raised_amount=("ipo_raised_amount", "max"),
        )
        .reset_index()
    )
    return summary


def build_features(raw_dir: Path) -> pd.DataFrame:
    tables = load_required_tables(raw_dir)
    organizations = build_base_organizations(tables["organizations"])
    funding = aggregate_funding_rounds(tables["funding_rounds"])
    early_funding = aggregate_early_funding_rounds(
        organizations, tables["funding_rounds"]
    )
    post_early_funding = aggregate_post_early_funding_rounds(
        organizations, tables["funding_rounds"]
    )
    investments = aggregate_investments(tables["investments"])
    acquisitions = aggregate_acquisitions(tables["acquisitions"])
    ipos = aggregate_ipos(tables["ipos"])

    dataset = organizations.merge(funding, on="org_id", how="left")
    dataset = dataset.merge(early_funding, on="org_id", how="left")
    dataset = dataset.merge(post_early_funding, on="org_id", how="left")
    dataset = dataset.merge(investments, on="org_id", how="left")
    dataset = dataset.merge(acquisitions, on="org_id", how="left")
    dataset = dataset.merge(ipos, on="org_id", how="left")

    numeric_fill_zero = [
        "funding_total_usd_org",
        "num_funding_rounds",
        "total_raised_usd_rounds",
        "avg_raised_usd_round",
        "max_raised_usd_round",
        "avg_participants",
        "max_participants",
        "early_num_funding_rounds",
        "early_total_raised_usd",
        "early_avg_raised_usd",
        "early_max_raised_usd",
        "early_avg_participants",
        "early_max_participants",
        "post_early_num_funding_rounds",
        "post_early_total_raised_usd",
        "post_early_avg_participants",
        "num_investment_rows",
        "unique_investor_count",
        "acquisition_count",
        "max_acquisition_price_usd",
        "ipo_count",
        "max_ipo_valuation",
        "max_ipo_raised_amount",
    ]
    for column in numeric_fill_zero:
        if column in dataset.columns:
            dataset[column] = pd.to_numeric(dataset[column], errors="coerce").fillna(0)

    for column in [
        "acquisition_count",
        "ipo_count",
        "num_funding_rounds",
        "early_num_funding_rounds",
        "post_early_num_funding_rounds",
    ]:
        if column not in dataset.columns:
            dataset[column] = 0

    dataset["is_acquired"] = dataset["acquisition_count"].gt(0).astype(int)
    dataset["is_ipo"] = dataset["ipo_count"].gt(0).astype(int)
    dataset["received_funding"] = dataset["num_funding_rounds"].gt(0).astype(int)
    dataset["successful_exit"] = (
        dataset["is_acquired"].eq(1) | dataset["is_ipo"].eq(1)
    ).astype(int)
    dataset["early_received_funding"] = dataset["early_num_funding_rounds"].gt(0).astype(int)
    dataset["future_received_funding"] = (
        dataset["post_early_num_funding_rounds"].gt(0).astype(int)
    )

    dataset["company_age_years"] = (
        REFERENCE_DATE - pd.to_datetime(dataset["founded_at"], errors="coerce")
    ).dt.days.div(365.25)
    dataset["time_to_first_round_days"] = (
        pd.to_datetime(dataset["first_round_at"], errors="coerce")
        - pd.to_datetime(dataset["founded_at"], errors="coerce")
    ).dt.days
    dataset["time_between_first_last_round_days"] = (
        pd.to_datetime(dataset["last_round_at"], errors="coerce")
        - pd.to_datetime(dataset["first_round_at"], errors="coerce")
    ).dt.days
    dataset["description_length"] = dataset["description"].fillna("").astype(str).str.len()
    dataset["snapshot_available"] = (
        pd.to_datetime(dataset["founded_at"], errors="coerce")
        <= (REFERENCE_DATE - pd.Timedelta(days=EARLY_SIGNAL_WINDOW_DAYS))
    ).astype(int)

    dataset["outcome_label"] = "OPERATING"
    dataset.loc[dataset["received_funding"].eq(1), "outcome_label"] = "FUNDED_NO_EXIT"
    dataset.loc[dataset["is_acquired"].eq(1), "outcome_label"] = "ACQUIRED"
    dataset.loc[dataset["is_ipo"].eq(1), "outcome_label"] = "IPO"
    dataset["model_target_exit"] = dataset["successful_exit"]
    dataset["model_target_funded"] = dataset["received_funding"]
    dataset["model_target_future_funding"] = dataset["future_received_funding"]
    dataset["early_stage_snapshot_days"] = EARLY_SIGNAL_WINDOW_DAYS

    ordered_columns = [
        "org_id",
        "name",
        "category",
        "country",
        "state",
        "city",
        "founded_at",
        "founded_year",
        "company_age_years",
        "description",
        "description_length",
        "status",
        "funding_total_usd_org",
        "num_funding_rounds",
        "total_raised_usd_rounds",
        "avg_raised_usd_round",
        "max_raised_usd_round",
        "avg_participants",
        "max_participants",
        "early_num_funding_rounds",
        "early_total_raised_usd",
        "early_avg_raised_usd",
        "early_max_raised_usd",
        "early_avg_participants",
        "early_max_participants",
        "early_first_round_at",
        "early_last_round_at",
        "early_latest_round_type",
        "post_early_num_funding_rounds",
        "post_early_total_raised_usd",
        "post_early_avg_participants",
        "post_early_first_round_at",
        "first_round_at",
        "last_round_at",
        "latest_round_type",
        "num_investment_rows",
        "unique_investor_count",
        "acquisition_count",
        "first_acquired_at",
        "last_acquired_at",
        "max_acquisition_price_usd",
        "ipo_count",
        "first_public_at",
        "last_public_at",
        "max_ipo_valuation",
        "max_ipo_raised_amount",
        "time_to_first_round_days",
        "time_between_first_last_round_days",
        "early_received_funding",
        "snapshot_available",
        "early_stage_snapshot_days",
        "received_funding",
        "future_received_funding",
        "is_acquired",
        "is_ipo",
        "successful_exit",
        "model_target_exit",
        "model_target_funded",
        "model_target_future_funding",
        "outcome_label",
    ]

    existing_columns = [column for column in ordered_columns if column in dataset.columns]
    remaining_columns = [column for column in dataset.columns if column not in existing_columns]
    return dataset[existing_columns + remaining_columns]


def main():
    parser = argparse.ArgumentParser(
        description="Prepare a company-level startup outcome dataset from Crunchbase-style CSVs."
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=DEFAULT_RAW_DIR,
        help="Directory containing raw CSV files such as organizations.csv and funding_rounds.csv.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path for the processed company-level feature table.",
    )
    args = parser.parse_args()

    features = build_features(args.raw_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(args.output, index=False)

    print(f"Saved processed dataset to {args.output}")
    print(f"Rows: {len(features)}")
    print(f"Columns: {len(features.columns)}")
    print(features["outcome_label"].value_counts(dropna=False).to_string())


if __name__ == "__main__":
    main()
