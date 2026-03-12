def write_quality_dlq(failed_df, dlq_path: str):
    """
    Write failed quality records to Delta.

    Parameters
    ----------
    failed_df : DataFrame
        DataFrame containing failed quality records
    dlq_path : str
        Output Delta path for quality DLQ
    """

    if failed_df is None:
        return

    if failed_df.head(1):
        (
            failed_df.write
            .format("delta")
            .mode("append")
            .save(dlq_path)
        )