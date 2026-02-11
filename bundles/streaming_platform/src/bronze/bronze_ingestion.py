# Databricks notebook source
# COMMAND ----------

# ====== Job widgets (minimal) ======
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

# Read widgets
env = dbutils.widgets.get("env").strip() or "dev"
tenant_id = dbutils.widgets.get("tenant_id").strip() or "tenant_demo"
site_id = dbutils.widgets.get("site_id").strip() or "site_demo"
event_type = dbutils.widgets.get("event_type").strip() or "temp_humidity.v1"
config_file = dbutils.widgets.get("config_file").strip() or "configs/tenants/tenant_demo/dev.yml"
run_minutes = int(dbutils.widgets.get("run_minutes") or "5")

print(f"[runner params] env={env} tenant_id={tenant_id} site_id={site_id} event_type={event_type} run_minutes={run_minutes}")
print(f"[runner params] config_file={config_file}")

# COMMAND ----------

# ====== Load tenant config (80/20) ======
import yaml
import os

#with open(config_file, "r") as f:
#    cfg = yaml.safe_load(f) or {}

cfg_path = os.path.join(os.getcwd(), config_file)
with open(cfg_path, "r") as f:
    cfg = yaml.safe_load(f)

# Override from config (single source of truth)
tenant_id = cfg["tenant"]["tenant_id"]
site_id = cfg["tenant"].get("site_id_default", site_id)

allowed_event_types = cfg["events"]["allowed_event_types"]
if not allowed_event_types:
    raise Exception("Config error: events.allowed_event_types is empty")

# For Project 01 we run ONE event_type per run:
event_type = allowed_event_types[0]

# If config defines run_minutes, let it override widget default
run_minutes = int(cfg.get("runtime", {}).get("run_minutes", run_minutes))

print(f"[runner config] tenant_id={tenant_id} site_id={site_id} event_type={event_type} run_minutes={run_minutes}")
print(f"[runner config] allowed_event_types={allowed_event_types}")

# COMMAND ----------

# Delegate to your existing WORKSPACE Bronze logic notebook
# Keep this as the ONLY thing in this cell for Databricks %run stability
%run "/Users/info@justaboutdata.com/streaming-platform/bronze/bronze_ingestion"
