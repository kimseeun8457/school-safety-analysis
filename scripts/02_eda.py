"""Perform exploratory data analysis on elementary-school accident data."""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from typing import Final

MPL_CACHE_DIR = Path(tempfile.gettempdir()) / "school_safety_analysis_mpl"
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
INPUT_PATH: Final[Path] = (
    PROJECT_ROOT / "data" / "processed" / "accident_clean.csv"
)
FIGURES_DIR: Final[Path] = PROJECT_ROOT / "outputs" / "figures"
TABLES_DIR: Final[Path] = PROJECT_ROOT / "outputs" / "tables"
MISSING_CATEGORY: Final[str] = "미상"
TOP_CATEGORY_COUNT: Final[int] = 15
WEEKDAY_ORDER: Final[list[str]] = ["월", "화", "수", "목", "금", "토", "일"]

VARIABLE_LABELS: Final[dict[str, str]] = {
    "occurrence_year": "사고 연도",
    "occurrence_month": "사고 월",
    "grade": "학년",
    "gender": "성별",
    "weekday": "사고 요일",
    "activity_period": "사고 시간",
    "occurrence_hour": "사고 발생 시각(시)",
    "place": "사고 장소",
    "accident_type": "사고 형태",
    "activity": "사고 당시 활동",
    "body_part": "사고 부위",
}

SUMMARY_COLUMNS: Final[list[str]] = list(VARIABLE_LABELS)
CROSS_TABLE_PAIRS: Final[tuple[tuple[str, str], ...]] = (
    ("place", "accident_type"),
    ("place", "activity"),
    ("activity", "accident_type"),
    ("activity_period", "place"),
    ("activity_period", "activity"),
    ("grade", "place"),
    ("grade", "accident_type"),
)


def configure_visual_style() -> None:
    """Configure logging and plot defaults for Korean-language EDA outputs."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams["font.family"] = "AppleGothic"
    plt.rcParams["axes.unicode_minus"] = False


def load_accident_data(input_path: Path) -> pd.DataFrame:
    """Load and validate preprocessed accident data.

    Args:
        input_path: Path to ``accident_clean.csv``.

    Returns:
        Validated accident data.

    Raises:
        FileNotFoundError: If the preprocessed input is absent.
        ValueError: If required columns are missing or no records are available.
    """
    required_columns = {
        "occurrence_year_month",
        "occurrence_time",
        "grade",
        "gender",
        "weekday",
        "activity_period",
        "place",
        "accident_type",
        "activity",
        "body_part",
    }
    if not input_path.is_file():
        raise FileNotFoundError(f"Preprocessed input does not exist: {input_path}")

    data = pd.read_csv(input_path, encoding="utf-8-sig", dtype="string")
    missing_columns = sorted(required_columns - set(data.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    if data.empty:
        raise ValueError("Preprocessed accident data is empty")

    logging.info("Loaded %s accident records", len(data))
    return data


def prepare_eda_data(data: pd.DataFrame) -> pd.DataFrame:
    """Create time-based variables used by EDA without changing source records.

    Args:
        data: Validated preprocessed accident data.

    Returns:
        Copy of data with year, month, and hour variables for EDA.
    """
    prepared = data.copy()
    year_month = pd.to_datetime(
        prepared["occurrence_year_month"],
        format="%Y-%m",
        errors="coerce",
    )
    occurrence_time = pd.to_datetime(
        prepared["occurrence_time"],
        format="%H:%M",
        errors="coerce",
    )
    prepared["occurrence_year"] = year_month.dt.year.astype("Int64").astype("string")
    prepared["occurrence_month"] = year_month.dt.month.astype("Int64").astype("string")
    prepared["occurrence_hour"] = occurrence_time.dt.hour.astype("Int64").astype(
        "string"
    )
    for column in SUMMARY_COLUMNS:
        prepared[column] = prepared[column].fillna(MISSING_CATEGORY)
    return prepared


def category_counts(data: pd.DataFrame, column: str) -> pd.DataFrame:
    """Calculate counts and proportions for a categorical variable.

    Args:
        data: Prepared EDA data.
        column: Categorical column to summarize.

    Returns:
        Category-level count and proportion table.
    """
    counts = (
        data[column]
        .fillna(MISSING_CATEGORY)
        .astype("string")
        .value_counts(dropna=False)
        .rename_axis("category")
        .reset_index(name="count")
    )
    counts.insert(0, "variable", column)
    counts["proportion"] = counts["count"] / len(data)
    return counts


def create_eda_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Create a long-form frequency summary for all EDA variables.

    Args:
        data: Prepared EDA data.

    Returns:
        Combined category frequencies and proportions.
    """
    return pd.concat(
        [category_counts(data, column) for column in SUMMARY_COLUMNS],
        ignore_index=True,
    )


def create_cross_tables(data: pd.DataFrame) -> pd.DataFrame:
    """Create long-form cross tables for planned EDA variable pairs.

    Args:
        data: Prepared EDA data.

    Returns:
        Combined cross-table cell counts for all planned variable pairs.
    """
    tables: list[pd.DataFrame] = []
    for left_column, right_column in CROSS_TABLE_PAIRS:
        table = pd.crosstab(data[left_column], data[right_column])
        long_table = (
            table.rename_axis(index=left_column, columns=right_column)
            .stack()
            .rename("count")
            .reset_index()
            .rename(
                columns={
                    left_column: "value_x",
                    right_column: "value_y",
                }
            )
        )
        long_table.insert(0, "variable_y", right_column)
        long_table.insert(0, "variable_x", left_column)
        tables.append(long_table)
    return pd.concat(tables, ignore_index=True)


def plot_count(
    axis: plt.Axes,
    counts: pd.DataFrame,
    title: str,
    horizontal: bool = False,
) -> None:
    """Draw a count plot from a category summary.

    Args:
        axis: Matplotlib axis for the chart.
        counts: Category count table.
        title: Chart title.
        horizontal: Whether to use horizontal bars.
    """
    positions = range(len(counts))
    if horizontal:
        axis.barh(positions, counts["count"], color="#4C78A8")
        axis.set_yticks(list(positions), labels=counts["category"])
        axis.invert_yaxis()
        axis.set_xlabel("사고 건수")
        axis.set_ylabel("")
    else:
        axis.bar(positions, counts["count"], color="#4C78A8")
        axis.set_xticks(list(positions), labels=counts["category"])
        axis.set_xlabel("")
        axis.set_ylabel("사고 건수")
        axis.tick_params(axis="x", rotation=45)
    axis.set_title(title)


def ordered_counts(data: pd.DataFrame, column: str) -> pd.DataFrame:
    """Sort chronological EDA categories while preserving unknown values last.

    Args:
        data: Prepared EDA data.
        column: One of the chronological categorical variables.

    Returns:
        Ordered category count table.
    """
    counts = category_counts(data, column)
    if column == "weekday":
        order = WEEKDAY_ORDER + [MISSING_CATEGORY]
        counts["_order"] = pd.Categorical(counts["category"], categories=order)
        return counts.sort_values("_order").drop(columns="_order")

    numeric_order = pd.to_numeric(counts["category"], errors="coerce")
    counts["_order"] = numeric_order.fillna(float("inf"))
    return counts.sort_values("_order").drop(columns="_order")


def save_accident_distribution(data: pd.DataFrame, output_path: Path) -> None:
    """Save combined year, month, weekday, and hour distributions.

    Args:
        data: Prepared EDA data.
        output_path: Destination PNG path.
    """
    figure, axes = plt.subplots(2, 2, figsize=(16, 10))
    for axis, column in zip(
        axes.flat,
        ("occurrence_year", "occurrence_month", "weekday", "occurrence_hour"),
    ):
        plot_count(axis, ordered_counts(data, column), VARIABLE_LABELS[column])
    figure.suptitle("초등학교 안전사고 발생 분포", fontsize=16)
    figure.tight_layout()
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)


def save_category_distribution(
    data: pd.DataFrame,
    column: str,
    output_path: Path,
) -> None:
    """Save a category distribution plot, limiting high-cardinality charts.

    Args:
        data: Prepared EDA data.
        column: Categorical variable to plot.
        output_path: Destination PNG path.
    """
    counts = category_counts(data, column)
    if len(counts) > TOP_CATEGORY_COUNT:
        counts = counts.head(TOP_CATEGORY_COUNT)
        title = f"{VARIABLE_LABELS[column]} 상위 {TOP_CATEGORY_COUNT}개"
    else:
        title = VARIABLE_LABELS[column]

    figure, axis = plt.subplots(figsize=(12, 8))
    plot_count(axis, counts, title, horizontal=len(counts) > 8)
    figure.tight_layout()
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)


def save_gender_distribution(data: pd.DataFrame, output_path: Path) -> None:
    """Save a pie chart for accident counts by gender.

    Args:
        data: Prepared EDA data.
        output_path: Destination PNG path.
    """
    counts = category_counts(data, "gender")
    figure, axis = plt.subplots(figsize=(8, 6))
    axis.pie(
        counts["count"],
        labels=counts["category"],
        autopct="%.1f%%",
        startangle=90,
    )
    axis.set_title("성별 사고 분포")
    figure.tight_layout()
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)


def save_heatmap(
    data: pd.DataFrame,
    left_column: str,
    right_column: str,
    output_path: Path,
) -> None:
    """Save a readable heatmap for the top categories of a cross table.

    Args:
        data: Prepared EDA data.
        left_column: Variable represented on heatmap rows.
        right_column: Variable represented on heatmap columns.
        output_path: Destination PNG path.
    """
    table = pd.crosstab(data[left_column], data[right_column])
    row_order = table.sum(axis=1).nlargest(TOP_CATEGORY_COUNT).index
    column_order = table.sum(axis=0).nlargest(TOP_CATEGORY_COUNT).index
    display_table = table.loc[row_order, column_order]

    figure, axis = plt.subplots(figsize=(14, 10))
    sns.heatmap(display_table, cmap="Blues", ax=axis)
    axis.set_title(
        f"{VARIABLE_LABELS[left_column]} × {VARIABLE_LABELS[right_column]} "
        f"(상위 {TOP_CATEGORY_COUNT}개 범주)"
    )
    axis.set_xlabel(VARIABLE_LABELS[right_column])
    axis.set_ylabel(VARIABLE_LABELS[left_column])
    figure.tight_layout()
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)


def save_outputs(data: pd.DataFrame) -> None:
    """Save EDA tables and figures to the project output directories.

    Args:
        data: Prepared EDA data.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    create_eda_summary(data).to_csv(
        TABLES_DIR / "eda_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )
    create_cross_tables(data).to_csv(
        TABLES_DIR / "eda_cross_table.csv",
        index=False,
        encoding="utf-8-sig",
    )

    save_accident_distribution(data, FIGURES_DIR / "accident_distribution.png")
    save_category_distribution(data, "grade", FIGURES_DIR / "grade_distribution.png")
    save_gender_distribution(data, FIGURES_DIR / "gender_distribution.png")
    save_category_distribution(data, "place", FIGURES_DIR / "place_distribution.png")
    save_category_distribution(
        data,
        "activity",
        FIGURES_DIR / "activity_distribution.png",
    )
    save_category_distribution(
        data,
        "accident_type",
        FIGURES_DIR / "accident_type_distribution.png",
    )
    save_category_distribution(
        data,
        "body_part",
        FIGURES_DIR / "body_part_distribution.png",
    )
    save_category_distribution(
        data,
        "activity_period",
        FIGURES_DIR / "time_distribution.png",
    )
    for left_column, right_column in CROSS_TABLE_PAIRS:
        filename = f"eda_heatmap_{left_column}_{right_column}.png"
        save_heatmap(data, left_column, right_column, FIGURES_DIR / filename)

    logging.info("Saved EDA tables to %s and figures to %s", TABLES_DIR, FIGURES_DIR)


def main() -> None:
    """Run univariate and cross-tabulation EDA for accident records."""
    configure_visual_style()
    try:
        data = prepare_eda_data(load_accident_data(INPUT_PATH))
        save_outputs(data)
    except (FileNotFoundError, OSError, ValueError, pd.errors.ParserError) as error:
        logging.error("EDA failed: %s", error)
        raise


if __name__ == "__main__":
    main()
