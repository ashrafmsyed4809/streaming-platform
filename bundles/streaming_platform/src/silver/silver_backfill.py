# Databricks notebook source
# COMMAND ----------
# ============================================
# SILVER BACKFILL (Project 04)
# Replay / Backfill from Bronze -> Silver
# ============================================

import yaml
from delta.tables import DeltaTable
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *

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

print(f"[silver_backfill] env={env}")
print(f"[silver_backfill] tenant_id(widget)={tenant_id_widget}")
print(f"[silver_backfill] config_file={config_file}")
print(f"[silver_backfill] start_date={start_date}")
print(f"[silver_backfill] end_date={end_date}")
print(f"[silver_backfill] event_types_raw={event_types_raw}")
print(f"[silver_backfill] replay_mode={replay_mode}")
print(f"[silver_backfill] apply_changes={apply_changes}")

if not start_date or not end_date:
    raise Exception("start_date and end_date are required for silver backfill")

# COMMAND ----------
# ============================================
# Bundle-safe config load
# ============================================

ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
nb_ws_path = ctx.notebookPath().get()

bundle_ws_root = nb_ws_path.split("/src/")[0]
bundle_local_root = "/Workspace" + bundle_ws_root
config_local_path = f"{bundle_local_root}/{config_file}"

print(f"[silver_backfill] notebookPath={nb_ws_path}")
print(f"[silver_backfill] bundle_ws_root={bundle_ws_root}")
print(f"[silver_backfill] config_local_path={config_local_path}")

with open(config_local_path, "r") as f:
    cfg = yaml.safe_load(f) or {}

tenant_cfg = cfg.get("tenant", {}) or {}
storage_cfg = cfg.get("storage", {}) or {}
events_cfg = cfg.get("events", {}) or {}

tenant_id = tenant_cfg.get("tenant_id") or tenant_id_widget
site_id = tenant_cfg.get("site_id_default")
base_path = storage_cfg.get("base_path")
allowed_event_types = events_cfg.get("allowed_event_types") or []
contracts_dir = events_cfg.get("contracts_dir") or "configs/contracts"

if not tenant_id:
    raise Exception("tenant_id is required")
if not base_path:
    raise Exception("Config error: storage.base_path is missing")
if not allowed_event_types:
    raise Exception("Config error: events.allowed_event_types is empty")

selected_event_types = event_types_list if event_types_list else allowed_event_types

print(f"[silver_backfill] tenant_id(final)={tenant_id}")
print(f"[silver_backfill] site_id={site_id}")
print(f"[silver_backfill] base_path={base_path}")
print(f"[silver_backfill] allowed_event_types={allowed_event_types}")
print(f"[silver_backfill] selected_event_types={selected_event_types}")
print(f"[silver_backfill] contracts_dir={contracts_dir}")

# COMMAND ----------
# ============================================
# Paths
# ============================================

root = f"{base_path}/env={env}"

bronze_path = f"{root}/bronze_envelope_v2"
silver_path = f"{root}/silver"
silver_dlq_path = f"{root}/silver_dlq"

print(f"[silver_backfill] bronze_path={bronze_path}")
print(f"[silver_backfill] silver_path={silver_path}")
print(f"[silver_backfill] silver_dlq_path={silver_dlq_path}")

# COMMAND ----------
# ============================================
# Helpers
# ============================================

def load_contract_schema(contract_path: str) -> StructType:
    with open(contract_path, "r") as f:
        contract = yaml.safe_load(f) or {}

    fields = []
    for coldef in contract.get("fields", []):
        name = coldef["name"]
        dtype = coldef["type"]
        nullable = coldef.get("nullable", True)

        if dtype == "string":
            spark_type = StringType()
        elif dtype == "double":
            spark_type = DoubleType()
        elif dtype == "long":
            spark_type = LongType()
        elif dtype == "timestamp":
            spark_type = TimestampType()
        else:
            raise Exception(f"Unsupported type in contract: {dtype}")

        fields.append(StructField(name, spark_type, nullable))

    return StructType(fields)


def ensure_delta_path(path: str, df: DataFrame, partition_cols: list):
    """
    Create an empty Delta table with the same partitioning if path does not exist yet.
    """
    if df is None:
        return

    if not DeltaTable.isDeltaTable(spark, path):
        print(f"[silver_backfill] Initializing Delta path: {path}")
        (
            df.limit(0).write
            .format("delta")
            .mode("overwrite")
            .partitionBy(*partition_cols)
            .save(path)
        )


def delete_replay_slice(path: str, tenant_id: str, start_date: str, end_date: str, event_types: list):
    """
    Delete only the affected replay slice from an existing Delta table.
    Uses event_date as the replay key.
    """
    if not DeltaTable.isDeltaTable(spark, path):
        print(f"[silver_backfill] No Delta table at path yet, skip delete: {path}")
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

    print(f"[silver_backfill] DELETE path={path}")
    print(f"[silver_backfill] DELETE condition={condition.strip()}")

    dt.delete(condition)


def build_silver_backfill_df(df: DataFrame, event_types: list, contracts_dir: str, bundle_local_root: str):
    """
    Reuses the same contract-driven parsing/validation logic as live Silver,
    but in bounded batch mode for replay.
    """
    result_df = None
    dlq_df = None

    for et in event_types:
        contract_file = f"{bundle_local_root}/{contracts_dir}/{et}.yml"

        try:
            schema = load_contract_schema(contract_file)
            print(f"[silver_backfill] Loaded contract for {et}: {contract_file}")
        except Exception as e:
            print(f"[silver_backfill] Contract load failed for {et}: {e}")
            continue

        et_df = df.filter(col("event_type") == et)

        if et_df.rdd.isEmpty():
            print(f"[silver_backfill] No Bronze rows for {et}. Skipping.")
            continue

        parsed = et_df.withColumn("parsed", from_json(col("payload"), schema))

        for field in schema.fieldNames():
            parsed = parsed.withColumn(field, col("parsed").getField(field))

        parsed = parsed.drop("parsed")

        # Ensure replay key exists for downstream delete/filter safety
        if "event_date" not in parsed.columns:
            parsed = parsed.withColumn("event_date", to_date(col("event_time_utc")))

        required_fields = [f.name for f in schema.fields if not f.nullable]

        missing_req = None
        for rf in required_fields:
            c = col(rf).isNull()
            missing_req = c if missing_req is None else (missing_req | c)

        if missing_req is not None:
            valid = parsed.filter(~missing_req)
            invalid = (
                parsed.filter(missing_req)
                .withColumn("reason_code", lit("CONTRACT_VALIDATION_FAILED"))
            )
        else:
            valid = parsed
            invalid = parsed.limit(0).withColumn("reason_code", lit("CONTRACT_VALIDATION_FAILED"))

        result_df = valid if result_df is None else result_df.unionByName(valid, allowMissingColumns=True)
        dlq_df = invalid if dlq_df is None else dlq_df.unionByName(invalid, allowMissingColumns=True)

    return result_df, dlq_df

# COMMAND ----------
# ============================================
# Read Bronze as bounded batch
# ============================================

bronze_df = (
    spark.read.format("delta").load(bronze_path)
    .filter(col("tenant_id") == tenant_id)
    .filter(col("event_date").between(lit(start_date), lit(end_date)))
)

if selected_event_types:
    bronze_df = bronze_df.filter(col("event_type").isin(selected_event_types))

print(f"[silver_backfill] Bronze input rows={bronze_df.count()}")
bronze_df.groupBy("event_type").count().orderBy("event_type").show(truncate=False)

if bronze_df.rdd.isEmpty():
    raise Exception("No Bronze rows found for the requested replay scope")

# COMMAND ----------
# ============================================
# Build replayed Silver + Silver DLQ
# ============================================

result_df, dlq_df = build_silver_backfill_df(
    bronze_df,
    selected_event_types,
    contracts_dir,
    bundle_local_root
)

if result_df is not None:
    print(f"[silver_backfill] Silver replay output rows={result_df.count()}")
    result_df.groupBy("event_type").count().orderBy("event_type").show(truncate=False)
    result_df.printSchema()
else:
    print("[silver_backfill] result_df is None")

if dlq_df is not None:
    print(f"[silver_backfill] Silver DLQ replay rows={dlq_df.count()}")
    dlq_df.groupBy("event_type").count().orderBy("event_type").show(truncate=False)
else:
    print("[silver_backfill] dlq_df is None")

# COMMAND ----------
# ============================================
# Preview target slices before delete/write
# ============================================

if DeltaTable.isDeltaTable(spark, silver_path):
    silver_before = (
        spark.read.format("delta").load(silver_path)
        .filter(col("tenant_id") == tenant_id)
        .filter(col("event_date").between(lit(start_date), lit(end_date)))
        .filter(col("event_type").isin(selected_event_types))
    )
    print(f"[silver_backfill] Existing Silver rows in replay scope={silver_before.count()}")
    silver_before.groupBy("event_type").count().orderBy("event_type").show(truncate=False)
else:
    print("[silver_backfill] Silver table does not exist yet")

if DeltaTable.isDeltaTable(spark, silver_dlq_path):
    dlq_before = (
        spark.read.format("delta").load(silver_dlq_path)
        .filter(col("tenant_id") == tenant_id)
        .filter(col("event_date").between(lit(start_date), lit(end_date)))
        .filter(col("event_type").isin(selected_event_types))
    )
    print(f"[silver_backfill] Existing Silver DLQ rows in replay scope={dlq_before.count()}")
    dlq_before.groupBy("event_type").count().orderBy("event_type").show(truncate=False)
else:
    print("[silver_backfill] Silver DLQ table does not exist yet")

# COMMAND ----------
# ============================================
# Apply replay (delete + append) only if enabled
# ============================================

silver_partitions = ["tenant_id", "event_type", "source_id", "ingest_date"]
silver_dlq_partitions = ["tenant_id", "event_type", "source_id", "ingest_date"]

if not apply_changes:
    print("[silver_backfill] DRY RUN ONLY. No deletes or writes were applied.")
else:
    print("[silver_backfill] APPLY CHANGES = TRUE. Starting replay write...")

    # Ensure target tables exist before delete/write
    if result_df is not None:
        ensure_delta_path(silver_path, result_df, silver_partitions)
    if dlq_df is not None:
        ensure_delta_path(silver_dlq_path, dlq_df, silver_dlq_partitions)

    # Delete existing replay slice
    delete_replay_slice(silver_path, tenant_id, start_date, end_date, selected_event_types)
    delete_replay_slice(silver_dlq_path, tenant_id, start_date, end_date, selected_event_types)

    # Append rebuilt slice
    if result_df is not None and not result_df.rdd.isEmpty():
        (
            result_df.write
            .format("delta")
            .mode("append")
            .option("mergeSchema", "true")
            .partitionBy(*silver_partitions)
            .save(silver_path)
        )
        print("[silver_backfill] Silver replay write complete.")
    else:
        print("[silver_backfill] No Silver rows to write.")

    if dlq_df is not None and not dlq_df.rdd.isEmpty():
        (
            dlq_df.write
            .format("delta")
            .mode("append")
            .option("mergeSchema", "true")
            .partitionBy(*silver_dlq_partitions)
            .save(silver_dlq_path)
        )
        print("[silver_backfill] Silver DLQ replay write complete.")
    else:
        print("[silver_backfill] No Silver DLQ rows to write.")

# COMMAND ----------
# ============================================
# Post-run validation
# ============================================

if apply_changes and DeltaTable.isDeltaTable(spark, silver_path):
    silver_after = (
        spark.read.format("delta").load(silver_path)
        .filter(col("tenant_id") == tenant_id)
        .filter(col("event_date").between(lit(start_date), lit(end_date)))
        .filter(col("event_type").isin(selected_event_types))
    )

    print(f"[silver_backfill] Silver rows after replay={silver_after.count()}")
    silver_after.groupBy("event_type").count().orderBy("event_type").show(truncate=False)
    silver_after.select("tenant_id", "event_type", "source_id", "event_date", "ingest_date").distinct().show(50, truncate=False)

if apply_changes and DeltaTable.isDeltaTable(spark, silver_dlq_path):
    dlq_after = (
        spark.read.format("delta").load(silver_dlq_path)
        .filter(col("tenant_id") == tenant_id)
        .filter(col("event_date").between(lit(start_date), lit(end_date)))
        .filter(col("event_type").isin(selected_event_types))
    )

    print(f"[silver_backfill] Silver DLQ rows after replay={dlq_after.count()}")
    dlq_after.groupBy("event_type").count().orderBy("event_type").show(truncate=False)

print("[silver_backfill] DONE.")