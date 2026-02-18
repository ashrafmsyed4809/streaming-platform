# Streaming Platform – Runbook (Project 01)

This document explains how to deploy, run, monitor, and troubleshoot the Streaming Platform on Azure.

---

# 1. Platform Overview

Architecture:

Event Hub → Bronze → Silver → Gold  
Storage: ADLS Gen2 (Delta Lake)  
Compute: Databricks Jobs (Asset Bundles)  
Security: Managed Identity  

Environment structure:

abfss://streaming@<storage-account>.dfs.core.windows.net/platform/env=<env>/


Layers:

- bronze_envelope
- dlq_envelope
- silver
- silver_dlq
- gold
- checkpoints
- audit

---

# 2. Deployment (CI/CD)

Deployment uses Databricks Asset Bundles.

## Validate bundle

databricks bundle validate -t dev


## Deploy bundle

databricks bundle deploy -t dev


This deploys:
- Job definition
- Runner notebooks
- Config files
- Schemas
- Rules

Bundle workspace path:

/Workspace/Users/<user>/.bundle/streaming_platform/dev/files


---

# 3. Running the Job

The job consists of 3 tasks:

1. Bronze
2. Silver
3. Gold

Run from:

Databricks → Workflows → streaming_platform_dev → Run Now

Runtime parameters:

| Parameter | Description |
|------------|-------------|
| env | dev / stage / prod |
| tenant_id | Client identifier |
| config_file | YAML config path |
| run_minutes | 0 = continuous, >0 = POC duration |

Example:

run_minutes = 5


This runs the stream for 5 minutes and stops cleanly.

---

# 4. Storage Paths

Base path:

abfss://streaming@<storage>.dfs.core.windows.net/platform/env=<env>/


Bronze:

bronze_envelope/


DLQ:

dlq_envelope/



Silver:

silver/


Gold:

gold/device_minute/


Audit:

audit/audit_pipeline_batches


---

# 5. Viewing Logs

## Job logs

Databricks → Workflows → Job → Run → Output

Look for:


---

# 5. Viewing Logs

## Job logs

Databricks → Workflows → Job → Run → Output

Look for:


## DLQ Records

dlq_path = "abfss://.../dlq_envelope"
spark.read.format("delta").load(dlq_path).display()


## Audit Metrics

audit_path = "abfss://.../audit/audit_pipeline_batches"
spark.read.format("delta").load(audit_path).display()


Important fields:

- input_rows
- output_rows
- dlq_rows
- status
- error

---

# 6. Troubleshooting

## DLQ count = 0 but bad data sent

Check:
- Event Hub starting position
- parse_ok logic
- DLQ writer

## Authentication errors (Event Hub)

Verify:
- Connection string
- SAS policy permissions
- Event Hub name

## Storage errors

Ensure:
- Managed identity enabled
- DATA_SECURITY_MODE_DEDICATED cluster mode

---

# 7. Replay / Backfill

To replay data:

1. Stop job
2. Delete checkpoint folder
3. Restart job

Checkpoint path example:

checkpoints/gold/device_minute/<event_type>/


---

# 8. Production Mode

Set:

run_minutes = 0


This runs continuously.

---

End of Runbook.
