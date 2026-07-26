"""Summarize compensation severity for elementary-school accident categories."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Final

import pandas as pd


PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
INPUT_PATH: Final[Path] = (
    PROJECT_ROOT / "data" / "processed" / "compensation_clean.csv"
)
OUTPUT_DIR: Final[Path] = PROJECT_ROOT / "outputs" / "tables"
PAYMENT_COLUMNS: Final[list[str]] = [
    "medical_benefit",
    "disability_benefit",
    "care_benefit",
    "survivor_benefit",
    "funeral_expense",
    "consolation_payment",
    "preservation_cost",
]
GROUP_COLUMNS: Final[list[str]] = [
    "place",
    "accident_type",
    "activity",
    "body_part",
]


def configure_logging() -> None:
    """Configure consistent console logging for compensation analysis."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def load_compensation_data(input_path: Path) -> pd.DataFrame:
    """Load and validate cleaned compensation data.

    Args:
        input_path: Path to ``compensation_clean.csv``.

    Returns:
        Validated compensation data.

    Raises:
        FileNotFoundError: If the preprocessed compensation file is absent.
        ValueError: If required columns are missing or the data is invalid.
    """
    required_columns = set(PAYMENT_COLUMNS) | set(GROUP_COLUMNS)
    if not input_path.is_file():
        raise FileNotFoundError(f"Preprocessed input does not exist: {input_path}")

    data = pd.read_csv(input_path, encoding="utf-8-sig")
    missing_columns = sorted(required_columns - set(data.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    if data.empty:
        raise ValueError("Preprocessed compensation data is empty")
    if data[PAYMENT_COLUMNS].isna().any().any():
        raise ValueError("Compensation payment columns contain missing values")
    if (data[PAYMENT_COLUMNS] < 0).any().any():
        raise ValueError("Compensation payment columns contain negative values")

    logging.info("Loaded %s compensation records", len(data))
    return data


def add_total_compensation(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate the total compensation amount for each accident record.

    Args:
        data: Validated compensation data.

    Returns:
        Copy of data with a numeric ``total_compensation`` column.
    """
    enriched = data.copy()
    enriched["total_compensation"] = enriched[PAYMENT_COLUMNS].sum(axis=1)
    return enriched


def summarize_by_category(data: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """Calculate compensation distribution statistics for one category.

    Args:
        data: Compensation data with total compensation values.
        group_column: Categorical column used for grouping.

    Returns:
        Category-level count and compensation distribution statistics.
    """
    grouped = data.groupby(group_column, observed=True)["total_compensation"]
    summary = grouped.agg(
        record_count="count",
        total_compensation_sum="sum",
        mean_total_compensation="mean",
        median_total_compensation="median",
        max_total_compensation="max",
        std_total_compensation="std",
    ).reset_index()
    quantiles = grouped.quantile([0.25, 0.75]).unstack()
    quantiles = quantiles.rename(
        columns={0.25: "q1_total_compensation", 0.75: "q3_total_compensation"}
    ).reset_index()
    summary = summary.merge(quantiles, on=group_column, how="left")
    summary["iqr_total_compensation"] = (
        summary["q3_total_compensation"] - summary["q1_total_compensation"]
    )
    summary = summary.rename(columns={group_column: "category"})
    summary.insert(0, "group_variable", group_column)
    return summary.sort_values(
        ["median_total_compensation", "record_count"],
        ascending=False,
    ).reset_index(drop=True)


def create_severity_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Combine severity summaries for all planned compensation groupings.

    Args:
        data: Compensation data with total compensation values.

    Returns:
        Long-form severity summary for place, type, activity, and body part.
    """
    summaries = [summarize_by_category(data, column) for column in GROUP_COLUMNS]
    return pd.concat(summaries, ignore_index=True)


def create_overview(data: pd.DataFrame) -> pd.DataFrame:
    """Create an overall compensation overview for audit and reconciliation.

    Args:
        data: Compensation data with total compensation values.

    Returns:
        One-row overview of total compensation distribution statistics.
    """
    total_compensation = data["total_compensation"]
    return pd.DataFrame(
        [
            {
                "record_count": len(data),
                "total_compensation_sum": total_compensation.sum(),
                "mean_total_compensation": total_compensation.mean(),
                "median_total_compensation": total_compensation.median(),
                "max_total_compensation": total_compensation.max(),
                "std_total_compensation": total_compensation.std(),
                "q1_total_compensation": total_compensation.quantile(0.25),
                "q3_total_compensation": total_compensation.quantile(0.75),
                "iqr_total_compensation": (
                    total_compensation.quantile(0.75)
                    - total_compensation.quantile(0.25)
                ),
            }
        ]
    )


def save_results(
    severity_summary: pd.DataFrame,
    overview: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Save compensation severity tables to the project output directory.

    Args:
        severity_summary: Category-level severity distribution statistics.
        overview: Overall compensation distribution statistics.
        output_dir: Destination directory for CSV outputs.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    severity_summary.to_csv(
        output_dir / "severity_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )
    overview.to_csv(
        output_dir / "compensation_overview.csv",
        index=False,
        encoding="utf-8-sig",
    )
    logging.info("Saved compensation severity results to %s", output_dir)


def main() -> None:
    """Run compensation severity analysis for planned category groupings."""
    configure_logging()
    try:
        data = add_total_compensation(load_compensation_data(INPUT_PATH))
        severity_summary = create_severity_summary(data)
        overview = create_overview(data)
        save_results(severity_summary, overview, OUTPUT_DIR)
    except (FileNotFoundError, OSError, ValueError, pd.errors.ParserError) as error:
        logging.error("Compensation analysis failed: %s", error)
        raise


if __name__ == "__main__":
    main()
