# Onboarding a New Client (Phase 1 – Non-Franchise Model)

This guide explains how to onboard a new client using the reusable Streaming Platform framework.

The platform follows the 80/20 design:

- 80% core platform (reusable, shared)
- 20% client configuration (isolated via YAML, schemas, and rules)

No core code changes are required to onboard a new client.

---

# 1. Create Tenant Configuration

Create a new folder:

configs/tenants/<new_tenant_id>/

Example:

configs/tenants/tenant_acme/


Inside that folder, create:

- dev.yml
- stage.yml
- prod.yml

---

# 2. Define Client Configuration (Example dev.yml)


tenant:
  tenant_id: "tenant_acme"
  site_id_default: "site_001"

events:
  allowed_event_types:
    - temp_humidity.v1

storage:
  base_path: "abfss://streaming@<storage-account>.dfs.core.windows.net/platform"

ingestion:
  eventhub_name: "iot-sensor-events"
  consumer_group: "$Default"

runtime:
  run_minutes: 5

# 3. **Verify Schema Exists**

For each event_type listed in:

events.allowed_event_types


schemas/event_types/<event_type>.json

Example:

schemas/event_types/temp_humidity.v1.json

# 4. (Optional) Add Validation Rules

If custom validation is required:


rules/event_types/<event_type>.yml

Example:

required_fields:
  - device_id
  - timestamp_utc

# 5. Deploy to Databricks

From project root:


databricks bundle deploy -t dev

- This syncs:

    - Config files

    - Schemas

    - Rules

    - Job definitions

# 6. Run the Job

In Databricks:

Workflows → streaming_platform_dev → Run Now

Parameters:

| Parameter   | Value                               |
| ----------- | ----------------------------------- |
| tenant_id   | tenant_acme                         |
| config_file | configs/tenants/tenant_acme/dev.yml |
| run_minutes | 5                                   |

# 7. Data Isolation

All records include:

tenant_id

event_type

ingest_date

Data is partitioned by:

tenant_id / event_type / ingest_date

This ensures:

Logical isolation

Query performance

Multi-client scalability

No code branching per client is required.

# 8. Production Mode

For continuous production streaming:

Set:

run_minutes: 0

in prod.yml

Then deploy:


databricks bundle deploy -t prod

# Summary

Onboarding a new client requires:

1. Creating tenant YAML config

2. Ensuring schema exists

3. Deploying bundle

4. Running job

Core platform logic remains unchanged.


