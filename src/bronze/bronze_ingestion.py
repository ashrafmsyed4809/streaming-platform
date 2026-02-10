# Databricks notebook source
# COMMAND ----------

# Minimal widgets (do not rename your existing variables)
def _w(name: str, default: str):
    try:
        dbutils.widgets.get(name)
    except Exception:
        dbutils.widgets.text(name, default)

_w("env", "dev")
_w("tenant_id", "tenant_demo")
_w("site_id", "site_demo")
_w("event_type", "temp_humidity.v1")
_w("config_file", "configs/tenants/tenant_demo/dev.yml")
_w("run_minutes", "5")

print("[runner] Starting BRONZE. Delegating to existing Workspace notebook...")

# COMMAND ----------

# NOTE: This should point to your existing WORKSPACE bronze notebook (the one that already works)
%run "/Users/info@justaboutdata.com/streaming-platform/bronze/bronze_ingestion"
