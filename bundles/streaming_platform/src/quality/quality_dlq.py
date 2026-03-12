from pyspark.sql.functions import lit, current_timestamp, to_json, struct, col


def build_quality_dlq_df(df, rule_name: str, rule_type: str, rule_field: str):
    """
    Add metadata columns for quality-DLQ records.

    Parameters
    ----------
    df : DataFrame
        Failed Spark DataFrame
    rule_name : str
        Name of the failed rule
    rule_type : str
        Rule type (range, min_value, etc.)
    rule_field : str
        Field that failed validation

    Returns
    -------
    DataFrame
        DataFrame enriched for quality DLQ storage
    """

    payload_cols = [c for c in df.columns]

    dlq_df = (
        df.withColumn("rule_name", lit(rule_name))
          .withColumn("rule_type", lit(rule_type))
          .withColumn("rule_field", lit(rule_field))
          .withColumn("failed_value", col(rule_field).cast("string"))
          .withColumn("quality_check_ts", current_timestamp())
          .withColumn("payload_json", to_json(struct(*[col(c) for c in payload_cols])))
    )

    return dlq_df
