from pyspark.sql.functions import col

from src.quality.rule_loader import load_rules
from src.quality.rule_engine import apply_quality_rules


def run_quality_checks(
    spark,
    silver_df,
    event_type: str,
    rules_base_path: str
):
    """
    Apply quality rules to a Silver DataFrame.

    Parameters
    ----------
    spark : SparkSession
        Active Spark session
    silver_df : DataFrame
        Standardized Silver DataFrame
    event_type : str
        Event type name (ex: temp_humidity.v2)
    rules_base_path : str
        Path to rules/event_types directory

    Returns
    -------
    passed_df : DataFrame
        Records that passed all quality checks
    failed_df : DataFrame
        Records that failed one or more quality checks
    """

    rules = load_rules(event_type=event_type, rules_base_path=rules_base_path)

    passed_df, failed_df = apply_quality_rules(silver_df, rules)

    return passed_df, failed_df