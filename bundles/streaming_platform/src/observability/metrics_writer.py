from pyspark.sql import Row
from pyspark.sql.functions import current_timestamp


def write_observability_metrics(
    spark,
    metrics_path: str,
    tenant_id: str,
    event_type: str,
    layer: str,
    records_in: int,
    records_passed: int,
    records_failed: int,
    dlq_count: int
):
    """
    Write one observability metrics record to Delta.

    Parameters
    ----------
    spark : SparkSession
        Active Spark session
    metrics_path : str
        Output Delta path
    tenant_id : str
        Tenant identifier
    event_type : str
        Event type name
    layer : str
        Pipeline layer name (ex: quality)
    records_in : int
        Input record count
    records_passed : int
        Passed record count
    records_failed : int
        Failed record count
    dlq_count : int
        Number of records written to DLQ
    """

    metrics_row = Row(
        tenant_id=tenant_id,
        event_type=event_type,
        layer=layer,
        records_in=records_in,
        records_passed=records_passed,
        records_failed=records_failed,
        dlq_count=dlq_count
    )

    metrics_df = spark.createDataFrame([metrics_row]).withColumn(
        "batch_ts",
        current_timestamp()
    )

    (
        metrics_df.write
        .format("delta")
        .mode("append")
        .save(metrics_path)
    )