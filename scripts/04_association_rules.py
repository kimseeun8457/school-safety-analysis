"""Discover recurring elementary-school accident patterns with Apriori."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import pandas as pd
import yaml
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder


PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
INPUT_PATH: Final[Path] = (
    PROJECT_ROOT / "data" / "processed" / "accident_clean.csv"
)
CONFIG_PATH: Final[Path] = PROJECT_ROOT / "config" / "config.yaml"
OUTPUT_DIR: Final[Path] = PROJECT_ROOT / "outputs" / "association_rules"
MISSING_CATEGORY: Final[str] = "미상"


@dataclass(frozen=True)
class AprioriConfig:
    """Store validated Apriori analysis settings."""

    transaction_columns: list[str]
    min_support: float
    min_confidence: float
    min_lift: float


def configure_logging() -> None:
    """Configure consistent console logging for association-rule analysis."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def load_config(config_path: Path) -> AprioriConfig:
    """Load and validate Apriori settings from the project configuration.

    Args:
        config_path: Path to the project YAML configuration file.

    Returns:
        Validated Apriori settings.

    Raises:
        FileNotFoundError: If the configuration file is absent.
        ValueError: If required Apriori settings are missing or invalid.
    """
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file does not exist: {config_path}")

    with config_path.open(encoding="utf-8") as config_file:
        config_data = yaml.safe_load(config_file)
    rule_config = config_data.get("association_rules", {})
    transaction_columns = rule_config.get("transaction_columns", [])
    min_support = rule_config.get("min_support")
    min_confidence = rule_config.get("min_confidence")
    min_lift = rule_config.get("min_lift")

    if not isinstance(transaction_columns, list) or not transaction_columns:
        raise ValueError(
            "association_rules.transaction_columns must be a non-empty list"
        )
    for name, value in {
        "min_support": min_support,
        "min_confidence": min_confidence,
        "min_lift": min_lift,
    }.items():
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"association_rules.{name} must be greater than zero")

    return AprioriConfig(
        transaction_columns=transaction_columns,
        min_support=float(min_support),
        min_confidence=float(min_confidence),
        min_lift=float(min_lift),
    )


def load_accident_data(input_path: Path, columns: list[str]) -> pd.DataFrame:
    """Load accident data and validate Apriori transaction columns.

    Args:
        input_path: Path to the cleaned accident CSV file.
        columns: Source columns used to build transactions.

    Returns:
        Accident data containing all transaction columns.

    Raises:
        FileNotFoundError: If the cleaned accident file is absent.
        ValueError: If the data is empty or required columns are missing.
    """
    if not input_path.is_file():
        raise FileNotFoundError(f"Preprocessed input does not exist: {input_path}")

    data = pd.read_csv(input_path, encoding="utf-8-sig", dtype="string")
    missing_columns = sorted(set(columns) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Missing transaction columns: {missing_columns}")
    if data.empty:
        raise ValueError("Preprocessed accident data is empty")

    logging.info("Loaded %s accident records", len(data))
    return data


def create_transaction_matrix(
    data: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    """Convert accident records into a one-hot transaction matrix.

    Args:
        data: Cleaned accident data.
        columns: Variables that define one accident transaction.

    Returns:
        Boolean transaction matrix whose columns are ``variable=value`` items.
    """
    transactions = [
        [f"{column}={value}" for column, value in row.items()]
        for row in data.loc[:, columns].fillna(MISSING_CATEGORY).to_dict("records")
    ]
    encoder = TransactionEncoder()
    matrix = encoder.fit(transactions).transform(transactions)
    transaction_matrix = pd.DataFrame(matrix, columns=encoder.columns_)
    logging.info(
        "Created a transaction matrix with %s records and %s items",
        *transaction_matrix.shape,
    )
    return transaction_matrix


def serialize_itemset(items: frozenset[str]) -> str:
    """Create a stable text representation of a frequent itemset.

    Args:
        items: Itemset produced by Apriori.

    Returns:
        Alphabetically ordered item labels separated by `` | ``.
    """
    return " | ".join(sorted(items))


def find_frequent_itemsets(
    transaction_matrix: pd.DataFrame,
    min_support: float,
) -> pd.DataFrame:
    """Find frequent itemsets using the Apriori algorithm.

    Args:
        transaction_matrix: One-hot transaction matrix.
        min_support: Minimum transaction support for an itemset.

    Returns:
        Frequent itemsets with readable item labels.

    Raises:
        ValueError: If no itemsets meet the configured support threshold.
    """
    itemsets = apriori(
        transaction_matrix,
        min_support=min_support,
        use_colnames=True,
    )
    if itemsets.empty:
        raise ValueError("No frequent itemsets meet the configured support threshold")

    result = itemsets.copy()
    result["itemset"] = result["itemsets"].map(serialize_itemset)
    result["item_count"] = result["itemsets"].map(len)
    result = result.drop(columns="itemsets").sort_values(
        ["item_count", "support"],
        ascending=[False, False],
    )
    logging.info("Found %s frequent itemsets", len(result))
    return result.reset_index(drop=True)


def find_association_rules(
    frequent_itemsets: pd.DataFrame,
    min_confidence: float,
    min_lift: float,
) -> pd.DataFrame:
    """Generate and filter association rules from frequent itemsets.

    Args:
        frequent_itemsets: Apriori itemsets with support values.
        min_confidence: Minimum rule confidence.
        min_lift: Minimum rule lift.

    Returns:
        Rules with readable antecedents and consequents, sorted by strength.
    """
    source_itemsets = frequent_itemsets.loc[:, ["support", "itemset"]].copy()
    source_itemsets["itemsets"] = source_itemsets["itemset"].map(
        lambda value: frozenset(value.split(" | "))
    )
    source_itemsets = source_itemsets.drop(columns="itemset")
    rules = association_rules(
        source_itemsets,
        metric="confidence",
        min_threshold=min_confidence,
    )
    rules = rules.loc[rules["lift"] >= min_lift].copy()
    if rules.empty:
        return pd.DataFrame(
            columns=[
                "antecedents",
                "consequents",
                "support",
                "confidence",
                "lift",
                "leverage",
                "conviction",
            ]
        )

    rules["antecedents"] = rules["antecedents"].map(serialize_itemset)
    rules["consequents"] = rules["consequents"].map(serialize_itemset)
    result_columns = [
        "antecedents",
        "consequents",
        "support",
        "confidence",
        "lift",
        "leverage",
        "conviction",
    ]
    result = rules.loc[:, result_columns].sort_values(
        ["lift", "confidence", "support"],
        ascending=False,
    )
    logging.info("Found %s association rules", len(result))
    return result.reset_index(drop=True)


def save_results(
    itemsets: pd.DataFrame,
    rules: pd.DataFrame,
    config: AprioriConfig,
    output_dir: Path,
) -> None:
    """Save Apriori itemsets, rules, and run settings.

    Args:
        itemsets: Frequent itemsets produced by Apriori.
        rules: Filtered association rules.
        config: Applied Apriori settings.
        output_dir: Destination directory for analysis results.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    itemsets.to_csv(
        output_dir / "frequent_itemsets.csv",
        index=False,
        encoding="utf-8-sig",
    )
    rules.to_csv(
        output_dir / "association_rules.csv",
        index=False,
        encoding="utf-8-sig",
    )
    summary = pd.DataFrame(
        [
            {
                "transaction_columns": " | ".join(config.transaction_columns),
                "min_support": config.min_support,
                "min_confidence": config.min_confidence,
                "min_lift": config.min_lift,
                "frequent_itemset_count": len(itemsets),
                "association_rule_count": len(rules),
            }
        ]
    )
    summary.to_csv(
        output_dir / "association_rule_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )
    logging.info("Saved association-rule results to %s", output_dir)


def main() -> None:
    """Run Apriori frequent-itemset and association-rule analysis."""
    configure_logging()
    try:
        config = load_config(CONFIG_PATH)
        data = load_accident_data(INPUT_PATH, config.transaction_columns)
        transaction_matrix = create_transaction_matrix(
            data,
            config.transaction_columns,
        )
        itemsets = find_frequent_itemsets(transaction_matrix, config.min_support)
        rules = find_association_rules(
            itemsets,
            config.min_confidence,
            config.min_lift,
        )
        save_results(itemsets, rules, config, OUTPUT_DIR)
    except (
        FileNotFoundError,
        OSError,
        ValueError,
        pd.errors.ParserError,
        yaml.YAMLError,
    ) as error:
        logging.error("Association-rule analysis failed: %s", error)
        raise


if __name__ == "__main__":
    main()
