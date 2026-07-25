"""Test associations among elementary-school accident risk factors."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency


PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
INPUT_PATH: Final[Path] = (
    PROJECT_ROOT / "data" / "processed" / "accident_clean.csv"
)
OUTPUT_DIR: Final[Path] = PROJECT_ROOT / "outputs" / "tables"
ALPHA: Final[float] = 0.05
MISSING_CATEGORY: Final[str] = "미상"


@dataclass(frozen=True)
class AnalysisPair:
    """Define a pair of categorical variables for association testing."""

    left_column: str
    right_column: str


ANALYSIS_PAIRS: Final[tuple[AnalysisPair, ...]] = (
    AnalysisPair("place", "accident_type"),
    AnalysisPair("place", "activity"),
    AnalysisPair("activity", "accident_type"),
    AnalysisPair("grade", "place"),
    AnalysisPair("activity_period", "place"),
)


def configure_logging() -> None:
    """Configure consistent console logging for statistical analysis."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def load_accident_data(input_path: Path) -> pd.DataFrame:
    """Load and validate the preprocessed accident dataset.

    Args:
        input_path: Path to the cleaned accident CSV file.

    Returns:
        The validated accident dataset.

    Raises:
        FileNotFoundError: If the preprocessed input is absent.
        ValueError: If required analysis columns are missing or data is empty.
    """
    if not input_path.is_file():
        raise FileNotFoundError(f"Preprocessed input does not exist: {input_path}")

    data = pd.read_csv(input_path, encoding="utf-8-sig", dtype="string")
    required_columns = {
        column
        for pair in ANALYSIS_PAIRS
        for column in (pair.left_column, pair.right_column)
    }
    missing_columns = sorted(required_columns - set(data.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    if data.empty:
        raise ValueError("Preprocessed accident data is empty")

    logging.info("Loaded %s accident records", len(data))
    return data


def create_cross_table(
    data: pd.DataFrame,
    pair: AnalysisPair,
) -> pd.DataFrame:
    """Create a contingency table for an analysis pair.

    Args:
        data: Preprocessed accident data.
        pair: Pair of categorical variables to cross-tabulate.

    Returns:
        A contingency table whose rows and columns are category values.

    Raises:
        ValueError: If either variable has fewer than two categories.
    """
    subset = data[[pair.left_column, pair.right_column]].copy()
    subset = subset.fillna(MISSING_CATEGORY)
    table = pd.crosstab(subset[pair.left_column], subset[pair.right_column])
    if table.shape[0] < 2 or table.shape[1] < 2:
        raise ValueError(
            f"Insufficient categories for {pair.left_column} and {pair.right_column}"
        )
    return table


def calculate_cramers_v(
    chi_square: float,
    sample_size: int,
    table: pd.DataFrame,
) -> float:
    """Calculate Cramér's V for a contingency table.

    Args:
        chi_square: Chi-square test statistic.
        sample_size: Number of observations represented in the table.
        table: Contingency table used in the chi-square test.

    Returns:
        Cramér's V effect size.
    """
    minimum_dimension = min(table.shape) - 1
    if sample_size == 0 or minimum_dimension == 0:
        return float("nan")
    return float(np.sqrt(chi_square / (sample_size * minimum_dimension)))


def analyze_pair(
    data: pd.DataFrame,
    pair: AnalysisPair,
) -> tuple[dict[str, object], pd.DataFrame]:
    """Run a chi-square test and calculate Cramér's V for one variable pair.

    Args:
        data: Preprocessed accident data.
        pair: Pair of categorical variables to test.

    Returns:
        A result record and its long-form cross table.
    """
    cross_table = create_cross_table(data, pair)
    chi_square, p_value, degrees_of_freedom, _ = chi2_contingency(cross_table)
    sample_size = int(cross_table.to_numpy().sum())
    is_significant = bool(p_value < ALPHA)
    cramers_v = (
        calculate_cramers_v(chi_square, sample_size, cross_table)
        if is_significant
        else float("nan")
    )

    result = {
        "variable_x": pair.left_column,
        "variable_y": pair.right_column,
        "sample_size": sample_size,
        "chi_square": float(chi_square),
        "degrees_of_freedom": int(degrees_of_freedom),
        "p_value": float(p_value),
        "alpha": ALPHA,
        "is_significant": is_significant,
        "cramers_v": cramers_v,
    }
    long_cross_table = (
        cross_table.rename_axis(index=pair.left_column, columns=pair.right_column)
        .stack()
        .rename("count")
        .reset_index()
        .rename(
            columns={
                pair.left_column: "value_x",
                pair.right_column: "value_y",
            }
        )
    )
    long_cross_table.insert(0, "variable_y", pair.right_column)
    long_cross_table.insert(0, "variable_x", pair.left_column)

    logging.info(
        "%s × %s: chi-square=%.2f, p-value=%.4g, significant=%s",
        pair.left_column,
        pair.right_column,
        chi_square,
        p_value,
        is_significant,
    )
    return result, long_cross_table


def save_results(
    chi_square_results: pd.DataFrame,
    cross_tables: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Save statistical-test summaries and cross tables.

    Args:
        chi_square_results: Results of chi-square tests and effect sizes.
        cross_tables: Combined long-form contingency table values.
        output_dir: Directory for table outputs.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    cramers_v_results = chi_square_results.loc[
        :, ["variable_x", "variable_y", "sample_size", "cramers_v", "is_significant"]
    ]

    chi_square_results.to_csv(
        output_dir / "chi_square_result.csv",
        index=False,
        encoding="utf-8-sig",
    )
    cramers_v_results.to_csv(
        output_dir / "cramers_v_result.csv",
        index=False,
        encoding="utf-8-sig",
    )
    cross_tables.to_csv(
        output_dir / "cross_table.csv",
        index=False,
        encoding="utf-8-sig",
    )
    chi_square_results.to_csv(
        output_dir / "statistical_test.csv",
        index=False,
        encoding="utf-8-sig",
    )
    logging.info("Saved statistical outputs to %s", output_dir)


def main() -> None:
    """Run all planned categorical association tests."""
    configure_logging()
    try:
        data = load_accident_data(INPUT_PATH)
        results: list[dict[str, object]] = []
        cross_tables: list[pd.DataFrame] = []
        for pair in ANALYSIS_PAIRS:
            result, cross_table = analyze_pair(data, pair)
            results.append(result)
            cross_tables.append(cross_table)

        save_results(
            chi_square_results=pd.DataFrame(results),
            cross_tables=pd.concat(cross_tables, ignore_index=True),
            output_dir=OUTPUT_DIR,
        )
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        logging.error("Statistical analysis failed: %s", error)
        raise


if __name__ == "__main__":
    main()
