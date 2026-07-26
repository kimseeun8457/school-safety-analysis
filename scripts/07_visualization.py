"""Visualize PPS rankings and prepare prevention-priority candidates."""

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
INPUT_PATH: Final[Path] = PROJECT_ROOT / "outputs" / "pps" / "pps_result.csv"
FIGURES_DIR: Final[Path] = PROJECT_ROOT / "outputs" / "figures"
PPS_DIR: Final[Path] = PROJECT_ROOT / "outputs" / "pps"
TOP_CONTEXT_COUNT: Final[int] = 20
REQUIRED_COLUMNS: Final[list[str]] = [
    "사고장소",
    "사고당시활동",
    "사고형태",
    "발생빈도",
    "Frequency Score",
    "Association Score",
    "Severity Score",
    "PPS",
    "PPS Rank",
]


def configure_visual_style() -> None:
    """Configure logging and non-interactive Korean plot defaults."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams["font.family"] = "AppleGothic"
    plt.rcParams["axes.unicode_minus"] = False


def load_pps_data(input_path: Path) -> pd.DataFrame:
    """Load and validate the PPS result table.

    Args:
        input_path: Path to the PPS ranking CSV file.

    Returns:
        PPS results sorted in descending score order.

    Raises:
        FileNotFoundError: If the PPS result file is absent.
        ValueError: If required columns are missing or data is empty.
    """
    if not input_path.is_file():
        raise FileNotFoundError(f"PPS result does not exist: {input_path}")

    data = pd.read_csv(input_path, encoding="utf-8-sig")
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    if data.empty:
        raise ValueError("PPS result is empty")
    return data.sort_values("PPS", ascending=False).reset_index(drop=True)


def add_context_label(data: pd.DataFrame) -> pd.DataFrame:
    """Create a readable label for each PPS risk context.

    Args:
        data: PPS results.

    Returns:
        PPS results with a risk-context label.
    """
    labeled = data.copy()
    labeled["위험상황"] = (
        labeled["사고장소"]
        + " | "
        + labeled["사고당시활동"]
        + " | "
        + labeled["사고형태"]
    )
    return labeled


def save_top_pps_chart(data: pd.DataFrame, output_path: Path) -> None:
    """Save a horizontal chart of the top PPS risk contexts.

    Args:
        data: Labeled PPS results.
        output_path: Destination PNG path.
    """
    top_contexts = data.head(TOP_CONTEXT_COUNT).iloc[::-1]
    figure, axis = plt.subplots(figsize=(14, 10))
    axis.barh(top_contexts["위험상황"], top_contexts["PPS"], color="#4C78A8")
    axis.set_title(f"PPS 상위 {TOP_CONTEXT_COUNT}개 위험상황")
    axis.set_xlabel("PPS")
    axis.set_ylabel("위험상황")
    figure.tight_layout()
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)


def save_component_chart(data: pd.DataFrame, output_path: Path) -> None:
    """Save a component comparison chart for top PPS risk contexts.

    Args:
        data: Labeled PPS results.
        output_path: Destination PNG path.
    """
    top_contexts = data.head(TOP_CONTEXT_COUNT).iloc[::-1]
    positions = list(range(len(top_contexts)))
    bar_height = 0.24
    figure, axis = plt.subplots(figsize=(14, 10))
    axis.barh(
        [position - bar_height for position in positions],
        top_contexts["Frequency Score"],
        height=bar_height,
        label="Frequency Score",
        color="#4C78A8",
    )
    axis.barh(
        positions,
        top_contexts["Association Score"],
        height=bar_height,
        label="Association Score",
        color="#F58518",
    )
    axis.barh(
        [position + bar_height for position in positions],
        top_contexts["Severity Score"],
        height=bar_height,
        label="Severity Score",
        color="#54A24B",
    )
    axis.set_yticks(positions, labels=top_contexts["위험상황"])
    axis.set_title(f"PPS 상위 {TOP_CONTEXT_COUNT}개 위험상황의 구성요소")
    axis.set_xlabel("정규화 점수")
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)


def save_pps_distribution(data: pd.DataFrame, output_path: Path) -> None:
    """Save the distribution of PPS values across risk contexts.

    Args:
        data: PPS results.
        output_path: Destination PNG path.
    """
    figure, axis = plt.subplots(figsize=(10, 6))
    sns.histplot(data=data, x="PPS", bins=40, ax=axis, color="#4C78A8")
    axis.set_title("위험상황별 PPS 분포")
    axis.set_xlabel("PPS")
    axis.set_ylabel("위험상황 수")
    figure.tight_layout()
    figure.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(figure)


def create_policy_candidates(data: pd.DataFrame) -> pd.DataFrame:
    """Create non-prescriptive prevention-priority candidates from top PPS rows.

    Args:
        data: Labeled PPS results.

    Returns:
        Top PPS contexts with a context-specific prevention review statement.
    """
    candidates = data.head(TOP_CONTEXT_COUNT).copy()
    candidates["정책검토방향"] = candidates.apply(
        lambda row: (
            f"{row['사고장소']}에서 {row['사고당시활동']} 활동 중 "
            f"{row['사고형태']} 위험상황을 우선 점검"
        ),
        axis=1,
    )
    return candidates.loc[
        :,
        [
            "PPS Rank",
            "위험상황",
            "사고장소",
            "사고당시활동",
            "사고형태",
            "발생빈도",
            "PPS",
            "정책검토방향",
        ],
    ]


def save_outputs(data: pd.DataFrame) -> None:
    """Save final PPS visualizations and prevention-priority candidates.

    Args:
        data: Labeled PPS results.
    """
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    PPS_DIR.mkdir(parents=True, exist_ok=True)
    save_top_pps_chart(data, FIGURES_DIR / "pps_top_contexts.png")
    save_component_chart(data, FIGURES_DIR / "pps_component_comparison.png")
    save_pps_distribution(data, FIGURES_DIR / "pps_distribution.png")
    create_policy_candidates(data).to_csv(
        PPS_DIR / "policy_recommendations.csv",
        index=False,
        encoding="utf-8-sig",
    )
    logging.info("Saved PPS visualizations and policy candidates")


def main() -> None:
    """Run final PPS visualization and policy-candidate generation."""
    configure_visual_style()
    try:
        save_outputs(add_context_label(load_pps_data(INPUT_PATH)))
    except (FileNotFoundError, OSError, ValueError, pd.errors.ParserError) as error:
        logging.error("Visualization failed: %s", error)
        raise


if __name__ == "__main__":
    main()
