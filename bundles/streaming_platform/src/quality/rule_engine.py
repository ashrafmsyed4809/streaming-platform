from functools import reduce

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, lit, to_timestamp
from src.quality.quality_dlq import build_quality_dlq_df


def _build_rule_condition(rule):
    rule_type = rule["type"]
    field = rule["field"]
    allow_null = rule.get("allow_null", False)

    if rule_type == "required":
        condition = col(field).isNotNull()

    elif rule_type == "between":
        min_val = rule["min"]
        max_val = rule["max"]
        condition = (col(field) >= min_val) & (col(field) <= max_val)

    elif rule_type == "optional":
        condition = lit(True)

    elif rule_type == "timestamp":
        condition = to_timestamp(col(field)).isNotNull()

    else:
        raise ValueError(f"Unsupported rule type: {rule_type}")

    if allow_null:
        condition = col(field).isNull() | condition

    return condition


def apply_quality_rules(df: DataFrame, rules: list):
    """
    Apply quality rules and return:
      - passed_df: rows that passed all rules
      - failed_df: rows that failed one or more rules, with DLQ metadata
    """

    if not rules:
        empty_failed_df = df.limit(0)
        return df, empty_failed_df

    pass_conditions = []
    failed_dfs = []

    for rule in rules:
        condition = _build_rule_condition(rule)
        pass_conditions.append(condition)

        rule_failed_df = df.filter(~condition)

        rule_failed_df = build_quality_dlq_df(
            rule_failed_df,
            rule_name=rule["name"],
            rule_type=rule["type"],
            rule_field=rule["field"]
        )

        failed_dfs.append(rule_failed_df)

    combined_pass_condition = reduce(lambda a, b: a & b, pass_conditions)
    passed_df = df.filter(combined_pass_condition)

    failed_df = failed_dfs[0]
    for extra_failed_df in failed_dfs[1:]:
        failed_df = failed_df.unionByName(extra_failed_df)

    return passed_df, failed_df