"""Merge elementary-school records from annual raw CSV files.

Usage:
    python scripts/merge_elementary_school_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUTS = [PROJECT_ROOT / "data/raw" / f"{year}.csv" for year in (2023, 2024, 2025)]
OUTPUT = PROJECT_ROOT / "data/processed/elementary_school_compensation_2023_2025_.csv"


def main() -> None:
    expected_fields: list[str] | None = None
    total_rows = 0
    kept_rows = 0
    seen_ids: set[str] = set()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as out_file:
        writer: csv.DictWriter | None = None
        for input_path in INPUTS:
            with input_path.open("r", encoding="utf-8-sig", newline="") as in_file:
                reader = csv.DictReader(in_file)
                if reader.fieldnames is None:
                    raise ValueError(f"Header missing: {input_path}")
                if expected_fields is None:
                    expected_fields = reader.fieldnames
                    writer = csv.DictWriter(out_file, fieldnames=expected_fields)
                    writer.writeheader()
                elif reader.fieldnames != expected_fields:
                    raise ValueError(f"Headers differ: {input_path}")

                for row in reader:
                    total_rows += 1
                    if row["학교급"] != "초등학교":
                        continue
                    record_id = row["구분"]
                    if record_id in seen_ids:
                        raise ValueError(f"Duplicate record ID: {record_id}")
                    seen_ids.add(record_id)
                    writer.writerow(row)
                    kept_rows += 1

    print(f"output={OUTPUT}")
    print(f"input_rows={total_rows}")
    print(f"elementary_rows={kept_rows}")
    print(f"unique_ids={len(seen_ids)}")


if __name__ == "__main__":
    main()
