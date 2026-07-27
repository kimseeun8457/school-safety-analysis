"""초등학교 안전사고 유형별 보상수준을 분석, 요약"""

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
    """보상 분석에 사용할 일관적인 콘솔 로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def load_compensation_data(input_path: Path) -> pd.DataFrame:
    """
    전처리된 보상 데이터의 유효성을 검증한다.

    함수에 전달하는 입력값: compensation_clean.csv 파일
    반환값: 유효성 검사를 통과한 보상 데이터(DataFrame)
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
    """
    사고별 총 보상금액을 계산한다.

    함수에 전달하는 입력값: 유효성 검사를 통과한 보상 데이터(DataFrame)

    반환값: total_compensation(총 보상금액) 컬럼이 추가된 데이터(DataFrame)
    """
    enriched = data.copy()
    enriched["total_compensation"] = enriched[PAYMENT_COLUMNS].sum(axis=1)
    return enriched


def summarize_by_category(data: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """ 하나의 범주형 변수에 대한 보상금 분포 통계를 계산한다.

    함수에 전달하는 입력값:
    - 총 보상금액(total_compensation)이 포함된 보상 데이터(DataFrame)
    - 그룹화에 사용할 범주형 변수명(group_column)
    반환값: 범주별 사고 건수와 보상금 분포 통계 데이터(DataFrame)
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
    """ 범주별 보상 심각도 요약 정보를 생성.
    함수에 전달하는 입력값: 총 보상금액(total_compensation)이 포함된 보상 데이터(DataFrame)
    반환값: 사고장소, 사고형태, 사고당시활동, 사고부위별 보상 심각도 요약 데이터(DataFrame)
    """
    summaries = [summarize_by_category(data, column) for column in GROUP_COLUMNS]
    return pd.concat(summaries, ignore_index=True)

def create_overview(data: pd.DataFrame) -> pd.DataFrame:
    """보상 데이터의 전체 현황을 요약하여 검토 및 데이터 확인에 활용한다.
    입력값: 총 보상금액(total_compensation)이 포함된 보상 데이터(DataFrame)
    반환값: 전체 보상금 분포 통계를 요약한 1행 데이터(DataFrame)
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
    """ 보상 심각도 분석 결과를 CSV 파일로 저장한다.
    입력값:
    - 범주별 보상 심각도 분포 통계 데이터(severity_summary)
    - 전체 보상금 분포 통계 데이터(overview)
    - CSV 파일을 저장할 출력 폴더 경로(output_dir)
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
