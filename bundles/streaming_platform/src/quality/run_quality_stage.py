from src.quality.quality_runner import run_quality_checks
from src.quality.quality_writer import write_quality_dlq
from src.observability.metrics_writer import write_observability_metrics


def run_quality_stage(
    spark,
    silver_df,
    tenant_id: str,
    event_type: str,
    rules_base_path: str,
    quality_dlq_path: str,
    observability_path: str
):
    """
    Run the Project 05 quality stage:
      1. Apply quality rules
      2. Write failed rows to quality DLQ
      3. Write observability metrics
      4. Return passed rows for Gold

    Returns
    -------
    passed_df : DataFrame
        Records that passed quality checks
    failed_df : DataFrame
        Records that failed one or more quality rules
    """

    passed_df, failed_df = run_quality_checks(
        spark=spark,
        silver_df=silver_df,
        event_type=event_type,
        rules_base_path=rules_base_path
    )

    write_quality_dlq(
        failed_df=failed_df,
        dlq_path=quality_dlq_path
    )

    records_in = silver_df.count()
    records_passed = passed_df.count()
    records_failed = failed_df.count()
    dlq_count = records_failed

    write_observability_metrics(
        spark=spark,
        metrics_path=observability_path,
        tenant_id=tenant_id,
        event_type=event_type,
        layer="quality",
        records_in=records_in,
        records_passed=records_passed,
        records_failed=records_failed,
        dlq_count=dlq_count
    )
    print(f"[quality] tenant_id={tenant_id}")
    print(f"[quality] event_type={event_type}")
    print(f"[quality] records_in={records_in}")
    print(f"[quality] records_passed={records_passed}")
    print(f"[quality] records_failed={records_failed}")
    print(f"[quality] quality_dlq_path={quality_dlq_path}")
    print(f"[quality] observability_path={observability_path}")

    return passed_df, failed_df