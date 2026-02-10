# Databricks notebook source
# COMMAND ----------

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

print("[runner] Starting GOLD. Delegating to existing Workspace notebook...")

# COMMAND ----------

%run "/Users/info@justaboutdata.com/streaming-platform/gold/gold_serving"
