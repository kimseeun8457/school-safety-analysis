"""Clean elementary-school accident and compensation data for analysis."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Final

import pandas as pd


PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
RAW_DIR: Final[Path] = PROJECT_ROOT / "data" / "raw"
ACCIDENT_INPUT_DIR: Final[Path] = RAW_DIR / "accident"
COMPENSATION_INPUT_DIR: Final[Path] = RAW_DIR / "compensation"
PROCESSED_DIR: Final[Path] = PROJECT_ROOT / "data" / "processed"
MISSING_CATEGORY: Final[str] = "미상"
TIME_PATTERN: Final[re.Pattern[str]] = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")
PAYMENT_SUFFIXES: Final[tuple[str, ...]] = (
    "benefit",
    "expense",
    "payment",
    "cost",
)

ACCIDENT_COLUMNS: Final[dict[str, str]] = {
    "구분": "record_id",
    "지역": "region",
    "학교급": "school_level",
    "사고자구분": "participant_type",
    "사고자학년": "grade",
    "사고자성별": "gender",
    "사고연월": "occurrence_year_month",
    "사고발생시각": "occurrence_time",
    "사고요일": "weekday",
    "사고시간": "activity_period",
    "사고장소": "place",
    "사고부위": "body_part",
    "사고형태": "accident_type",
    "사고당시활동": "activity",
}

COMPENSATION_COLUMNS: Final[dict[str, str]] = {
    "구분": "record_id",
    "지역": "region",
    "학교급": "school_level",
    "사고자구분": "participant_type",
    "사고자학년": "grade",
    "사고자성별": "gender",
    "사고시간": "activity_period",
    "사고장소": "place",
    "사고부위": "body_part",
    "사고형태": "accident_type",
    "사고당시활동": "activity",
    "요양급여": "medical_benefit",
    "장해급여": "disability_benefit",
    "간병급여": "care_benefit",
    "유족급여": "survivor_benefit",
    "장례비": "funeral_expense",
    "위로금": "consolation_payment",
    "보전비용": "preservation_cost",
}


def configure_logging() -> None:
    """Configure consistent console logging for preprocessing."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def load_csv_files(input_dir: Path) -> pd.DataFrame:
    """Load and concatenate all UTF-8 CSV files in an input directory.

    Args:
        input_dir: Directory containing one or more source CSV files.

    Returns:
        Concatenated source data with string-typed columns.

    Raises:
        FileNotFoundError: If the directory or source CSV files are absent.
    """
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    csv_paths = sorted(input_dir.glob("*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found in: {input_dir}")

    frames: list[pd.DataFrame] = []
    for csv_path in csv_paths:
        frame = pd.read_csv(csv_path, encoding="utf-8-sig", dtype="string")
        logging.info("Loaded %s rows from %s", len(frame), csv_path.name)
        frames.append(frame)

    return pd.concat(frames, ignore_index=True)


def validate_columns(data: pd.DataFrame, column_mapping: dict[str, str]) -> None:
    """Validate that all required source columns are present.

    Args:
        data: Source data to validate.
        column_mapping: Required source-to-standardized column mapping.

    Raises:
        ValueError: If one or more required columns are missing.
    """
    missing_columns = sorted(set(column_mapping) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")


def normalize_text_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Strip leading and trailing whitespace from all string columns.

    Args:
        data: Data frame with standardized columns.

    Returns:
        A copy with trimmed string values.
    """
    normalized = data.copy()
    for column in normalized.columns:
        if pd.api.types.is_string_dtype(normalized[column]):
            normalized[column] = normalized[column].str.strip()
    return normalized


def filter_elementary_school(data: pd.DataFrame) -> pd.DataFrame:
    """Retain only elementary-school records.

    Args:
        data: Standardized accident or compensation data.

    Returns:
        Records whose school level is ``초등학교``.
    """
    filtered = data.loc[data["school_level"] == "초등학교"].copy()
    logging.info("Retained %s elementary-school records", len(filtered))
    return filtered


def remove_duplicate_records(data: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate source records by identifier, keeping the latest file row.

    Args:
        data: Filtered data containing a record identifier.

    Returns:
        Data without missing identifiers or duplicate record identifiers.
    """
    before_count = len(data)
    cleaned = data.dropna(subset=["record_id"]).copy()
    cleaned = cleaned.loc[cleaned["record_id"] != ""].copy()
    cleaned = cleaned.drop_duplicates(subset=["record_id"], keep="last")
    logging.info(
        "Removed %s records with missing or duplicate IDs",
        before_count - len(cleaned),
    )
    return cleaned


def fill_missing_categories(
    data: pd.DataFrame,
    excluded_columns: set[str],
) -> pd.DataFrame:
    """Keep missing categorical values as an explicit category.

    Args:
        data: Data with standardized columns.
        excluded_columns: Columns that must retain non-categorical missing values.

    Returns:
        A copy with categorical missing values replaced by ``미상``.
    """
    filled = data.copy()
    for column in filled.columns:
        if (
            column not in excluded_columns
            and pd.api.types.is_string_dtype(filled[column])
        ):
            filled[column] = filled[column].fillna(MISSING_CATEGORY)
            filled.loc[filled[column] == "", column] = MISSING_CATEGORY
    return filled


def standardize_year_month(data: pd.DataFrame) -> pd.DataFrame:
    """Validate the accident year-month field and mark invalid values as missing.

    Args:
        data: Accident data containing ``occurrence_year_month``.

    Returns:
        Accident data with ISO year-month strings or ``미상``.
    """
    standardized = data.copy()
    parsed = pd.to_datetime(
        standardized["occurrence_year_month"], format="%Y-%m", errors="coerce"
    )
    invalid_count = parsed.isna().sum()
    standardized["occurrence_year_month"] = parsed.dt.strftime("%Y-%m").fillna(
        MISSING_CATEGORY
    )
    logging.info(
        "Marked %s invalid or missing year-month values as unknown",
        invalid_count,
    )
    return standardized


def standardize_occurrence_time(data: pd.DataFrame) -> pd.DataFrame:
    """Validate accident occurrence times and mark invalid values as missing.

    Args:
        data: Accident data containing ``occurrence_time``.

    Returns:
        Accident data with valid ``HH:MM`` strings or ``미상``.
    """
    standardized = data.copy()
    valid_time = standardized["occurrence_time"].str.match(TIME_PATTERN, na=False)
    invalid_count = (~valid_time).sum()
    standardized.loc[~valid_time, "occurrence_time"] = MISSING_CATEGORY
    logging.info(
        "Marked %s invalid or missing occurrence times as unknown",
        invalid_count,
    )
    return standardized


def clean_accident_data(data: pd.DataFrame) -> pd.DataFrame:
    """Clean elementary-school accident data for downstream analysis.

    Args:
        data: Concatenated raw accident data.

    Returns:
        Deduplicated, standardized elementary-school accident data.
    """
    validate_columns(data, ACCIDENT_COLUMNS)
    cleaned = normalize_text_columns(data.rename(columns=ACCIDENT_COLUMNS))
    cleaned = filter_elementary_school(cleaned)
    cleaned = remove_duplicate_records(cleaned)
    cleaned = standardize_year_month(cleaned)
    cleaned = standardize_occurrence_time(cleaned)
    return fill_missing_categories(
        cleaned,
        excluded_columns={"record_id", "occurrence_year_month", "occurrence_time"},
    )


def convert_payment_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Convert compensation columns to numeric values without imputing missing data.

    Args:
        data: Compensation data with standardized payment columns.

    Returns:
        Data with numeric compensation columns.
    """
    converted = data.copy()
    payment_columns = [
        column
        for column in COMPENSATION_COLUMNS.values()
        if column.endswith(PAYMENT_SUFFIXES)
    ]
    for column in payment_columns:
        original = converted[column]
        numeric = pd.to_numeric(
            original.str.replace(",", "", regex=False).str.strip(), errors="coerce"
        )
        invalid_count = (original.notna() & original.ne("") & numeric.isna()).sum()
        if invalid_count:
            logging.warning("Found %s non-numeric values in %s", invalid_count, column)
        converted[column] = numeric.astype("Float64")
    return converted


def clean_compensation_data(data: pd.DataFrame) -> pd.DataFrame:
    """Clean elementary-school compensation data for severity analysis.

    Args:
        data: Concatenated raw compensation data.

    Returns:
        Deduplicated, standardized elementary-school compensation data.
    """
    validate_columns(data, COMPENSATION_COLUMNS)
    cleaned = normalize_text_columns(data.rename(columns=COMPENSATION_COLUMNS))
    cleaned = filter_elementary_school(cleaned)
    cleaned = remove_duplicate_records(cleaned)
    cleaned = fill_missing_categories(
        cleaned,
        excluded_columns={"record_id"}
        | {
            column
            for column in COMPENSATION_COLUMNS.values()
            if column.endswith(PAYMENT_SUFFIXES)
        },
    )
    return convert_payment_columns(cleaned)


def save_csv(data: pd.DataFrame, output_path: Path) -> None:
    """Save a cleaned data frame as a UTF-8 CSV file.

    Args:
        data: Cleaned data to save.
        output_path: Destination CSV path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False, encoding="utf-8-sig")
    logging.info("Saved %s rows to %s", len(data), output_path)


def main() -> None:
    """Run preprocessing for accident and compensation source data."""
    configure_logging()
    try:
        accident_data = clean_accident_data(load_csv_files(ACCIDENT_INPUT_DIR))
        compensation_data = clean_compensation_data(
            load_csv_files(COMPENSATION_INPUT_DIR)
        )
        save_csv(accident_data, PROCESSED_DIR / "accident_clean.csv")
        save_csv(compensation_data, PROCESSED_DIR / "compensation_clean.csv")
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        logging.error("Preprocessing failed: %s", error)
        raise


if __name__ == "__main__":
    main()
