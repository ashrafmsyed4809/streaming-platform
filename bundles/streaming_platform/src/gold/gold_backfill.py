# Databricks notebook source
# COMMAND ----------
# ============================================
# GOLD BACKFILL (Project 04)
# Replay / Backfill from Silver -> Gold
# ============================================

import yaml
from delta.tables import DeltaTable
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

# COMMAND ----------
# ============================================
# Widgets
# ============================================

def _w(name: str, default: str):
    try:
        dbutils.widgets.get(name)
    except Exception:
        dbutils.widgets.text(name, default)

_w("env", "dev")
_w("tenant_id", "tenant_demo")
_w("config_file", "configs/tenants/tenant_demo/dev.yml")
_w("start_date", "2026-03-10")
_w("end_date", "2026-03-10")
_w("event_types", "temp_humidity.v1,temp_humidity.v2")
_w("replay_mode", "true")
_w("apply_changes", "false")   # safety switch; use false first

env = (dbutils.widgets.get("env") or "dev").strip()
tenant_id_widget = (dbutils.widgets.get("tenant_id") or "").strip()
config_file = (dbutils.widgets.get("config_file") or "").strip()
start_date = (dbutils.widgets.get("start_date") or "").strip()
end_date = (dbutils.widgets.get("end_date") or "").strip()
event_types_raw = (dbutils.widgets.get("event_types") or "").strip()
replay_mode_raw = (dbutils.widgets.get("replay_mode") or "true").strip().lower()
apply_changes_raw = (dbutils.widgets.get("apply_changes") or "false").strip().lower()

replay_mode = replay_mode_raw == "true"
apply_changes = apply_changes_raw == "true"

event_types_list = [x.strip() for x in event_types_raw.split(",") if x.strip()]

print(f"[gold_backfill] env={env}")
print(f"[gold_backfill] tenant_id(widget)={tenant_id_widget}")
print(f"[gold_backfill] config_file={config_file}")
print(f"[gold_backfill] start_date={start_date}")
print(f"[gold_backfill] end_date={end_date}")
print(f"[gold_backfill] event_types_raw={event_types_raw}")
print(f"[gold_backfill] replay_mode={replay_mode}")
print(f"[gold_backfill] apply_changes={apply_changes}")

if not start_date or not end_date:
    raise Exception("start_date and end_date are required for gold backfill")

if not config_file.endswith(".yml"):
    raise Exception(f"config_file must end with .yml, got: {config_file}")

# COMMAND ----------
# ============================================
# Bundle-safe config load
# ============================================

ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
nb_ws_path = ctx.notebookPath().get()

bundle_ws_root = nb_ws_path.split("/src/")[0]
bundle_local_root = "/Workspace" + bundle_ws_root
config_local_path = f"{bundle_local_root}/{config_file}"

print(f"[gold_backfill] notebookPath={nb_ws_path}")
print(f"[gold_backfill] bundle_ws_root={bundle_ws_root}")
print(f"[gold_backfill] config_local_path={config_local_path}")

with open(config_local_path, "r") as f:
    cfg = yaml.safe_load(f) or {}

tenant_cfg = cfg.get("tenant", {}) or {}
storage_cfg = cfg.get("storage", {}) or {}
events_cfg = cfg.get("events", {}) or {}
gold_cfg = cfg.get("gold", {}) or {}

tenant_id = tenant_cfg.get("tenant_id") or tenant_id_widget
site_id = tenant_cfg.get("site_id_default")
base_path = storage_cfg.get("base_path")
allowed_event_types = events_cfg.get("allowed_event_types") or []

if not tenant_id:
    raise Exception("tenant_id is required")
if not base_path:
    raise Exception("Config error: storage.base_path is missing")
if not allowed_event_types:
    raise Exception("Config error: events.allowed_event_types is empty")

selected_event_types = event_types_list if event_types_list else allowed_event_types

print(f"[gold_backfill] tenant_id(final)={tenant_id}")
print(f"[gold_backfill] site_id={site_id}")
print(f"[gold_backfill] base_path={base_path}")
print(f"[gold_backfill] allowed_event_types={allowed_event_types}")
print(f"[gold_backfill] selected_event_types={selected_event_types}")

# COMMAND ----------
# ============================================
# Paths
# ============================================

def resolve_paths(base_path: str, env: str, cfg: dict):
    gold_cfg = cfg.get("gold", {}) or {}
    curated_sub = gold_cfg.get("curated", {}).get("output_subpath", "gold_curated")
    metrics_sub = gold_cfg.get("metrics", {}).get("output_subpath", "gold_metrics")

    return {
        "silver": f"{base_path}/env={env}/silver",
        "curated": f"{base_path}/env={env}/{curated_sub}",
        "metrics": f"{base_path}/env={env}/{metrics_sub}",
    }

paths = resolve_paths(base_path, env, cfg)

print(f"[gold_backfill] silver_path={paths['silver']}")
print(f"[gold_backfill] curated_path={paths['curated']}")
print(f"[gold_backfill] metrics_path={paths['metrics']}")

# COMMAND ----------
# ============================================
# Gold transform logic (shared replay-safe version)
# ============================================

CURATED_COLUMNS = [
    "tenant_id", "site_id", "source_id", "device_id",
    "event_type", "schema_version", "source_system",
    "event_id",
    "event_time_utc", "event_date", "ingest_time_utc", "ingest_date",
    "temperature_f", "humidity_pct",
    "attributes",
]

def build_gold_curated(silver_df: DataFrame) -> DataFrame:
    df = (
        silver_df
        .withColumn("event_time_utc", F.to_timestamp("event_time_utc"))
        .withColumn("event_date", F.to_date("event_time_utc"))
        .withColumn("ingest_time_utc", F.to_timestamp("ingest_time_utc"))
        .withColumn("ingest_date", F.to_date("ingest_date"))
    )

    # Strong dedupe using event_id
    if "event_id" in df.columns:
        df = df.dropDuplicates(["tenant_id", "event_type", "event_id"])
    else:
        df = df.dropDuplicates(
            ["tenant_id", "event_type", "source_id", "event_time_utc", "sequence_number"]
        )

    existing_cols = [c for c in CURATED_COLUMNS if c in df.columns]
    return df.select(*existing_cols)


def build_gold_metrics(curated_df: DataFrame, grain: str = "hour") -> DataFrame:
    if grain == "day":
        bucket_col = "event_day"
        bucket = F.to_date("event_time_utc")
    else:
        bucket_col = "event_hour"
        bucket = F.date_trunc("hour", F.col("event_time_utc"))

    df = (
        curated_df
        .withColumn(bucket_col, bucket)
        .withColumn("event_date", F.to_date("event_time_utc"))
    )

    return (
        df.groupBy(
            "tenant_id", "event_type", "source_id", "ingest_date", "event_date", bucket_col
        )
        .agg(
            F.count("*").alias("event_count"),
            F.avg("temperature_f").alias("avg_temperature_f"),
            F.min("temperature_f").alias("min_temperature_f"),
            F.max("temperature_f").alias("max_temperature_f"),
            F.avg("humidity_pct").alias("avg_humidity_pct"),
            F.min("humidity_pct").alias("min_humidity_pct"),
            F.max("humidity_pct").alias("max_humidity_pct"),
        )
    )

# COMMAND ----------
# ============================================
# Helpers
# ============================================

def ensure_delta_path(path: str, df: DataFrame, partition_cols: list):
    if df is None:
        return

    if not DeltaTable.isDeltaTable(spark, path):
        print(f"[gold_backfill] Initializing Delta path: {path}")
        (
            df.limit(0).write
            .format("delta")
            .mode("overwrite")
            .partitionBy(*partition_cols)
            .save(path)
        )

def delete_replay_slice(path: str, tenant_id: str, start_date: str, end_date: str, event_types: list):
    if not DeltaTable.isDeltaTable(spark, path):
        print(f"[gold_backfill] No Delta table at path yet, skip delete: {path}")
        return

    if not event_types:
        raise Exception("delete_replay_slice requires at least one event_type")

    dt = DeltaTable.forPath(spark, path)
    event_types_sql = ",".join([f"'{x}'" for x in event_types])

    condition = f"""
        tenant_id = '{tenant_id}'
        AND event_date >= DATE '{start_date}'
        AND event_date <= DATE '{end_date}'
        AND event_type IN ({event_types_sql})
    """

    print(f"[gold_backfill] DELETE path={path}")
    print(f"[gold_backfill] DELETE condition={condition.strip()}")

    dt.delete(condition)

# COMMAND ----------
# ============================================
# Read Silver as bounded batch
# ============================================

silver_df = (
    spark.read.format("delta").load(paths["silver"])
    .filter(F.col("tenant_id") == tenant_id)
    .filter(F.col("event_date").between(F.lit(start_date), F.lit(end_date)))
)

if selected_event_types:
    silver_df = silver_df.filter(F.col("event_type").isin(selected_event_types))

print(f"[gold_backfill] Silver input rows={silver_df.count()}")
silver_df.groupBy("event_type").count().orderBy("event_type").show(truncate=False)

if silver_df.rdd.isEmpty():
    raise Exception("No Silver rows found for the requested replay scope")

# COMMAND ----------
# ============================================
# Build replayed Gold curated + metrics
# ============================================

curated_df = build_gold_curated(silver_df)

if curated_df is not None:
    print(f"[gold_backfill] Curated replay output rows={curated_df.count()}")
    curated_df.groupBy("event_type").count().orderBy("event_type").show(truncate=False)
    curated_df.printSchema()
else:
    print("[gold_backfill] curated_df is None")

metrics_frames = []

for et in selected_event_types:
    et_curated = curated_df.filter(F.col("event_type") == et)

    if et_curated.rdd.isEmpty():
        print(f"[gold_backfill] No curated rows for {et}. Skipping metrics.")
        continue

    per_event_cfg = (gold_cfg.get("event_types") or {}).get(et, {})
    grain = (per_event_cfg.get("metrics") or {}).get("grain", "hour")

    et_metrics = build_gold_metrics(et_curated, grain=grain)
    metrics_frames.append(et_metrics)

metrics_df = None
for mdf in metrics_frames:
    metrics_df = mdf if metrics_df is None else metrics_df.unionByName(mdf, allowMissingColumns=True)

if metrics_df is not None:
    print(f"[gold_backfill] Metrics replay output rows={metrics_df.count()}")
    metrics_df.groupBy("event_type").count().orderBy("event_type").show(truncate=False)
    metrics_df.printSchema()
else:
    print("[gold_backfill] metrics_df is None")

# COMMAND ----------
# ============================================
# Preview target slices before delete/write
# ============================================

if DeltaTable.isDeltaTable(spark, paths["curated"]):
    curated_before = (
        spark.read.format("delta").load(paths["curated"])
        .filter(F.col("tenant_id") == tenant_id)
        .filter(F.col("event_date").between(F.lit(start_date), F.lit(end_date)))
        .filter(F.col("event_type").isin(selected_event_types))
    )
    print(f"[gold_backfill] Existing curated rows in replay scope={curated_before.count()}")
    curated_before.groupBy("event_type").count().orderBy("event_type").show(truncate=False)
else:
    print("[gold_backfill] Curated table does not exist yet")

if DeltaTable.isDeltaTable(spark, paths["metrics"]):
    metrics_before = (
        spark.read.format("delta").load(paths["metrics"])
        .filter(F.col("tenant_id") == tenant_id)
        .filter(F.col("event_date").between(F.lit(start_date), F.lit(end_date)))
        .filter(F.col("event_type").isin(selected_event_types))
    )
    print(f"[gold_backfill] Existing metrics rows in replay scope={metrics_before.count()}")
    metrics_before.groupBy("event_type").count().orderBy("event_type").show(truncate=False)
else:
    print("[gold_backfill] Metrics table does not exist yet")

# COMMAND ----------
# ============================================
# Apply replay (delete + append) only if enabled
# ============================================

curated_partitions = ["tenant_id", "event_type", "source_id", "ingest_date"]
metrics_partitions = ["tenant_id", "event_type", "ingest_date"]

if not apply_changes:
    print("[gold_backfill] DRY RUN ONLY. No deletes or writes were applied.")
else:
    print("[gold_backfill] APPLY CHANGES = TRUE. Starting replay write...")

    if curated_df is not None:
        ensure_delta_path(paths["curated"], curated_df, curated_partitions)
    if metrics_df is not None:
        ensure_delta_path(paths["metrics"], metrics_df, metrics_partitions)

    delete_replay_slice(paths["curated"], tenant_id, start_date, end_date, selected_event_types)
    delete_replay_slice(paths["metrics"], tenant_id, start_date, end_date, selected_event_types)

    if curated_df is not None and not curated_df.rdd.isEmpty():
        (
            curated_df.write
            .format("delta")
            .mode("append")
            .option("mergeSchema", "true")
            .partitionBy(*curated_partitions)
            .save(paths["curated"])
        )
        print("[gold_backfill] Curated replay write complete.")
    else:
        print("[gold_backfill] No curated rows to write.")

    if metrics_df is not None and not metrics_df.rdd.isEmpty():
        (
            metrics_df.write
            .format("delta")
            .mode("append")
            .option("mergeSchema", "true")
            .partitionBy(*metrics_partitions)
            .save(paths["metrics"])
        )
        print("[gold_backfill] Metrics replay write complete.")
    else:
        print("[gold_backfill] No metrics rows to write.")

# COMMAND ----------
# ============================================
# Post-run validation
# ============================================

if apply_changes and DeltaTable.isDeltaTable(spark, paths["curated"]):
    curated_after = (
        spark.read.format("delta").load(paths["curated"])
        .filter(F.col("tenant_id") == tenant_id)
        .filter(F.col("event_date").between(F.lit(start_date), F.lit(end_date)))
        .filter(F.col("event_type").isin(selected_event_types))
    )

    print(f"[gold_backfill] Curated rows after replay={curated_after.count()}")
    curated_after.groupBy("event_type").count().orderBy("event_type").show(truncate=False)
    curated_after.select("tenant_id", "event_type", "source_id", "event_date", "ingest_date").distinct().show(50, truncate=False)

if apply_changes and DeltaTable.isDeltaTable(spark, paths["metrics"]):
    metrics_after = (
        spark.read.format("delta").load(paths["metrics"])
        .filter(F.col("tenant_id") == tenant_id)
        .filter(F.col("event_date").between(F.lit(start_date), F.lit(end_date)))
        .filter(F.col("event_type").isin(selected_event_types))
    )

    print(f"[gold_backfill] Metrics rows after replay={metrics_after.count()}")
    metrics_after.groupBy("event_type").count().orderBy("event_type").show(truncate=False)
    metrics_after.select("tenant_id", "event_type", "source_id", "event_date", "ingest_date").distinct().show(50, truncate=False)

print("[gold_backfill] DONE.")