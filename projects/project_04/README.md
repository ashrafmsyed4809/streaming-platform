
# Project 04 — Replay / Backfill Capability

## Overview

This project adds **Replay / Backfill capability** to the streaming platform.

Replay allows the platform to **safely reprocess historical event windows** when:

* a data quality issue is discovered
* event contracts change
* platform bugs are fixed
* downstream aggregates need recomputation

The replay system is implemented **without modifying the core streaming engine**, preserving the platform’s **80/20 architecture**:

* **80% reusable platform engine**
* **20% configuration per tenant and event type**

Replay is implemented as **bounded batch jobs** that rebuild downstream layers from Bronze/Silver data.

---

# Architecture

The platform follows the Medallion architecture:

```
Azure Event Hub
      ↓
Bronze (Universal Envelope + DLQ)
      ↓
Silver (Validation + Standardization)
      ↓
Gold (Curated + Metrics)
```

Replay works by rebuilding downstream layers from upstream data:

```
Bronze → Silver Replay → Gold Replay
```

Replay is **deterministic and idempotent**.

---

# Replay Strategy

Replay is implemented using a **delete + rebuild pattern**.

For a given replay window:

```
tenant_id
event_date range
event_type list
```

the system performs:

1. Locate affected rows
2. Delete the affected slice
3. Recompute results from upstream data
4. Write corrected outputs
5. Validate post-write counts

This guarantees:

* no duplicates
* deterministic results
* safe recomputation

---

# Replay Parameters

Replay jobs accept the following parameters:

| Parameter       | Description               |
| --------------- | ------------------------- |
| `env`           | Deployment environment    |
| `tenant_id`     | Tenant to replay          |
| `config_file`   | Tenant configuration      |
| `start_date`    | Replay window start       |
| `end_date`      | Replay window end         |
| `event_types`   | Event types to replay     |
| `replay_mode`   | Enables replay mode       |
| `apply_changes` | Safety switch for dry-run |

---

# Safety Mechanism

Replay supports **dry-run mode**.

```
apply_changes = false
```

Dry-run performs:

* replay computation
* slice identification
* row counts
* validation preview

without modifying any data.

Actual replay occurs only when:

```
apply_changes = true
```

---

# Silver Replay

Silver replay:

1. Reads Bronze events by `event_date`
2. Applies contract-driven parsing
3. Rebuilds validated Silver records
4. Rewrites only the affected slice

Partitioning:

```
tenant_id
event_type
source_id
ingest_date
```

---

# Gold Replay

Gold replay rebuilds two datasets.

## Gold Curated

Event-level dataset used for downstream analytics.

Fields include:

```
tenant_id
site_id
source_id
device_id
event_type
event_id
event_time_utc
event_date
temperature_f
humidity_pct
```

Replay deletes and rebuilds only the affected slice.

---

## Gold Metrics

Aggregated metrics derived from curated events.

Metrics include:

```
event_count
avg_temperature_f
min_temperature_f
max_temperature_f
avg_humidity_pct
min_humidity_pct
max_humidity_pct
```

Metrics are recomputed per:

```
tenant_id
event_type
source_id
event_date
event_hour
```

---

# Replay Workflow

Replay is executed through a Databricks workflow.

```
streaming_platform_replay_job
```

Task sequence:

```
1. silver_backfill
2. gold_backfill
```

Silver replay must complete successfully before Gold replay begins.

---

# Example Replay Run

Example replay parameters:

```
env = dev_tenant_02
tenant_id = tenant_02
start_date = 2026-03-10
end_date = 2026-03-10
event_types = temp_humidity.v1,temp_humidity.v2
apply_changes = true
```

Result:

**Gold Curated**

```
temp_humidity.v1 = 65
temp_humidity.v2 = 65
total = 130
```

**Gold Metrics**

```
temp_humidity.v1 = 2
temp_humidity.v2 = 2
total = 4
```

Replay successfully replaced the historical slice.

---

# Key Design Principles

The replay system was designed to:

* remain **configuration-driven**
* avoid modifying the streaming engine
* support **schema evolution**
* support **multi-tenant environments**
* guarantee **idempotent recomputation**

---

# Platform Capabilities After Project 04

The streaming platform now supports:

| Capability               | Status |
| ------------------------ | ------ |
| Multi-tenant ingestion   | ✓      |
| Config-driven onboarding | ✓      |
| Schema evolution         | ✓      |
| DLQ handling             | ✓      |
| Curated datasets         | ✓      |
| Aggregated metrics       | ✓      |
| Replay / Backfill        | ✓      |

---

# Version

```
v1.3.0
```

Project 04 introduces replay/backfill capabilities to the platform.

---

# Next Steps

Future improvements may include:

* automated replay orchestration
* replay audit logging
* SLA monitoring
* replay lineage tracking

---

