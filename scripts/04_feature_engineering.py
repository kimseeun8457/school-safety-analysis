"""전처리된 사고 데이터를 모델 학습에 사용할 수 있도록 인코딩된 데이터셋을 생성하는 스크립트."""

from __future__ import annotations

import logging
import math
from pathlib import Path
from typing import Final

import pandas as pd

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
INPUT_PATH: Final[Path] = (
    PROJECT_ROOT / "data" / "processed" / "accident_clean.csv"
)
OUTPUT_PATH: Final[Path] = (
    PROJECT_ROOT / "data" / "processed" / "model_dataset.csv"
)
MISSING_CATEGORY: Final[str] = "미상"
OTHER_CATEGORY: Final[str] = "기타"
RARE_CATEGORY_RATE: Final[float] = 0.001

MODEL_FEATURE_COLUMNS: Final[list[str]] = [
    "region",
    "grade",
    "gender",
    "weekday",
    "activity_period",
    "place",
    "accident_type",
    "activity",
    "occurrence_year",
    "occurrence_month",
    "season",
]
CATEGORICAL_FEATURE_COLUMNS: Final[list[str]] = [
    "region",
    "grade",
    "gender",
    "weekday",
    "activity_period",
    "place",
    "accident_type",
    "activity",
    "season",
]

def configure_logging() -> None:
    """feature 엔지니어링을 위한 일관적인 콘솔 로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

def load_accident_data(input_path: Path) -> pd.DataFrame:
    """전처리된 사고데이터를 불러오고, 유효성을 검사합니다.
    함수에 전달하는 입력값: accident_clean.csv
    반환값: 유효성 검사를 통과한 사고데이터
    """
    required_columns = {
        "record_id",
        "occurrence_year_month",
        *CATEGORICAL_FEATURE_COLUMNS[:-1],
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

def add_calendar_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    year, month, and season features 컬럼을 사고데이터에 추가한다.
    함수에 전달하는 입력값: accident_clean.csv
    반환값: 사고데이터에 occurrence_year, occurrence_month, season 컬럼 추가한 df
    """
    featured = data.copy()
    year_month = pd.to_datetime(
        featured["occurrence_year_month"],
        format="%Y-%m",
        errors="coerce",
    )
    invalid_count = year_month.isna().sum()
    if invalid_count:
        raise ValueError(f"Found {invalid_count} invalid occurrence year-month values")

    featured["occurrence_year"] = year_month.dt.year.astype("int16")
    featured["occurrence_month"] = year_month.dt.month.astype("int8")
    featured["season"] = featured["occurrence_month"].map(
        {
            12: "겨울",
            1: "겨울",
            2: "겨울",
            3: "봄",
            4: "봄",
            5: "봄",
            6: "여름",
            7: "여름",
            8: "여름",
            9: "가을",
            10: "가을",
            11: "가을",
        }
    ).astype("string")
    return featured

def calculate_rare_category_threshold(data: pd.DataFrame) -> int:
    """
    전체 데이터 개수를 기준으로 최소 범주 빈도 기준을 계산한다.
    함수에 전달하는 입력값: 범주 빈도 기준을 계산할 dataframe
    반환값: 전체 데이터의 0.1% 이상인 최소 정수 빈도
    """
    return max(1, math.ceil(len(data) * RARE_CATEGORY_RATE))

def combine_rare_categories(data: pd.DataFrame, threshold: int) -> pd.DataFrame:
    """
    빈도가 낮은 범주형변수를 '기타'로 통합한다.
    ※ 의미 있는 결측값인 '미상'은 별도의 범주로 유지한다.
    함수에 전달하는 입력값: 데이터, 기준이 되는 최소빈도
    반환값: 빈도가 낮은 범주형변수를 '기타'로 통합한 데이터
    """
    combined = data.copy()
    for column in CATEGORICAL_FEATURE_COLUMNS:
        counts = combined[column].value_counts(dropna=False)
        rare_categories = counts.loc[counts < threshold].index
        rare_categories = rare_categories[rare_categories != MISSING_CATEGORY]
        rare_count = len(rare_categories)
        if rare_count:
            combined.loc[combined[column].isin(rare_categories), column] = (
                OTHER_CATEGORY
            )
        logging.info(
            "%s: merged %s categories below the %s-record threshold",
            column,
            rare_count,
            threshold,
        )
    return combined

def build_model_dataset(data: pd.DataFrame) -> pd.DataFrame:
    """
    모델 학습에 사용할 변수를 인코딩하고, 데이터 추적을 위해 레코드 식별자를 유지한다.
    반환값: 범주형 변수가 원-핫 인코딩된 수치형 모델 학습 데이터(DataFrame)
    """
    model_data = data.loc[:, ["record_id", *MODEL_FEATURE_COLUMNS]].copy()
    encoded_features = pd.get_dummies(
        model_data.loc[:, CATEGORICAL_FEATURE_COLUMNS],
        columns=CATEGORICAL_FEATURE_COLUMNS,
        dtype="int8",
    )
    numeric_features = model_data.loc[:, ["occurrence_year", "occurrence_month"]]
    dataset = pd.concat(
        [model_data.loc[:, ["record_id"]], numeric_features, encoded_features],
        axis=1,
    )

    # TODO: Add Risk Level only after its documented classification rule is approved.
    return dataset


def save_model_dataset(data: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False, encoding="utf-8-sig")
    logging.info("Saved %s rows and %s columns to %s", *data.shape, output_path)


def main() -> None:
    configure_logging()
    try:
        data = load_accident_data(INPUT_PATH)
        data = add_calendar_features(data)
        threshold = calculate_rare_category_threshold(data)
        logging.info(
            "Rare-category threshold: %s records (%.1f%% of %s records)",
            threshold,
            RARE_CATEGORY_RATE * 100,
            len(data),
        )
        data = combine_rare_categories(data, threshold)
        save_model_dataset(build_model_dataset(data), OUTPUT_PATH)
    except (FileNotFoundError, OSError, ValueError, pd.errors.ParserError) as error:
        logging.error("Feature engineering failed: %s", error)
        raise

if __name__ == "__main__":
    main()
