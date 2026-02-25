
# ✅ README.md

# Streaming Platform on Azure (Project 01) — Reusable 80/20 Framework

This repository contains a **production-style streaming data platform** built on Azure and Databricks, designed to be:

- **80% reusable platform engine**
- **20% configurable per client (tenant) and per event type (sensor/RFID)**

This platform supports both:

1. **Senior Data Engineering Portfolio Demonstration**
2. **Streaming Data Cleaning Business Foundation**

---

## 🎯 Platform Goals

• Build production-grade streaming pipelines  
• Support multi-client (multi-tenant) onboarding  
• Support multiple sensor/event data types  
• Enforce strong data quality and schema validation  
• Enable fast onboarding through configuration instead of code changes  
• Demonstrate real-world DevOps and CI/CD architecture  

---

## 🧱 Technology Stack

| Component | Technology |
|----------|------------|
| Streaming Ingestion | Azure Event Hub |
| Processing | Azure Databricks Structured Streaming |
| Storage | Azure Data Lake Storage Gen2 |
| Table Format | Delta Lake |
| Orchestration | Databricks Multi-Task Jobs |
| CI/CD | Databricks Asset Bundles (Deployed) + GitHub Actions (Next Step) |

---

# 🏗 Architecture Overview

Event Hub → Bronze → Silver → Gold  

All data is stored in Delta Lake with partitioning:

```

tenant_id / event_type / ingest_date

```

The platform includes:

✔ Config-driven onboarding  
✔ Multi-tenant support  
✔ DLQ (Dead Letter Queue) isolation  
✔ Audit metrics tracking  
✔ Managed identity secure compute  
✔ CI/CD via Databricks Asset Bundles  

---

## 📸 Platform Proof (Production Evidence)

### 1️⃣ Job Orchestration (Bronze → Silver → Gold)

![Job Success](docs/screenshots/project01/01-job-success.png)

---

### 2️⃣ Config-Driven Execution (Event Version Override)

YAML configuration enables onboarding new event versions without modifying core code.

![Runner Config Override](docs/screenshots/project01/02-runner-config-v2.png)

---

### 3️⃣ DLQ – Corrupt Event Isolation

Invalid JSON events are detected in Bronze and routed safely to Dead Letter Queue.

![DLQ Records](docs/screenshots/project01/03-dlq-table.png)

---

### 4️⃣ Observability – Audit Metrics

Each batch tracks:

- input_rows  
- output_rows  
- dlq_rows  
- latency metrics  
- job status  

![Audit Metrics](docs/screenshots/project01/04-audit-dlq-count.png)

---

### 5️⃣ Gold Layer (Serving Output)

Aggregated device metrics written to:

```

gold/device_minute/

```

![Gold Output](docs/screenshots/project01/05-gold-output.png)

---

## 📦 Universal Event Envelope (Contract-First Streaming)

All incoming streaming data follows a standardized envelope.

tenant_id  
site_id  
device_id  
device_type  
event_type  
event_id  
event_time_utc  
ingest_time_utc  
schema_version  
source_system  
payload  
attributes  

### Why This Matters

✔ Standardizes ingestion across sensor types  
✔ Enables reusable platform pipelines  
✔ Supports multi-client separation  
✔ Allows schema evolution  

---

## 🗄 Storage Layout (ADLS Medallion Architecture)

raw  
bronze  
dlq  
silver  
gold  
checkpoints  
audit  

### Partition Strategy

```

tenant_id / event_type / ingest_date

```

This improves:

• Query performance  
• Storage cost efficiency  
• Replay/backfill capabilities  

---

## 📂 Repository Structure

### 80% Reusable Platform Engine

```

src/
common/
bronze/
silver/
gold/

```

#### src/common
Shared utilities:
- Configuration loader
- Logging helpers
- Audit tracking
- Envelope validation

#### src/bronze
- Raw ingestion
- Envelope parsing
- DLQ routing
- Bronze table writes

#### src/silver
- Schema validation
- Data quality rules
- Enrichment hooks
- Clean standardized tables

#### src/gold
- Aggregations
- Merge/upsert serving tables
- Analytics-ready datasets

---

### 20% Configurable Surface

```

configs/
global/
tenants/

schemas/
event_types/

rules/
event_types/

```

#### configs/global
Platform default configuration.

#### configs/tenants
Per-client configuration files.

#### schemas/event_types
Payload schema definitions per event type.

#### rules/event_types
Data quality validation rules.

---

## 🧩 Multi-Client (Tenant) Support

Clients are separated using:

• `tenant_id` inside event envelope  
• Tenant-specific configuration  
• Tenant-based storage partitioning  

This enables:

✔ New sensors for existing client  
✔ New clients using same platform engine  

---

## 🚀 Onboarding Process

### Onboard New Event Type (Sensor / RFID / IoT Source)

1. Add schema file:
```

schemas/event_types/<event_type>.json

```

2. Add rule file:
```

rules/event_types/<event_type>.yml

```

3. Update tenant configuration:
```

configs/tenants/<tenant_id>/<environment>.yml

```

No core logic rewrite required.

---

### Onboard New Client

1. Create new folder:
```

configs/tenants/<new_tenant>/

```

2. Add:
- dev.yml
- stage.yml
- prod.yml

3. Deploy bundle:
```

databricks bundle deploy -t dev

```

Core platform remains unchanged.

---

## ⚙️ Runtime Execution (POC Mode)

Supports controlled test execution:

```

run_minutes = 5

```

Set to:

```

run_minutes = 0

```

for continuous production mode.

Pipeline execution order:

Bronze → Silver → Gold

---

## 📊 Observability & Monitoring

Audit tracking captures:

• Batch record counts  
• DLQ event counts  
• End-to-end latency  
• Job success/failure  
• Processing duration  

Audit table location:

```

audit/audit_pipeline_batches

```

---

## 🔄 CI/CD

### Implemented

✔ Databricks Asset Bundles  
✔ Multi-environment targets (dev/stage/prod)  
✔ Parameterized job execution  

### Next Step

➡ GitHub Actions automated deployment  

---

## 📘 Documentation

Located in `docs/` folder:

• runbook.md  
• onboarding_new_client.md  
• onboarding_new_event_type.md  
• platform_master_context.md  

---

## ⭐ Project Status

### Completed
✔ Repository architecture  
✔ Multi-tenant config structure  
✔ Universal event contract  
✔ Medallion storage layout  
✔ Bronze/Silver/Gold streaming  
✔ DLQ isolation with reason codes  
✔ Audit metrics tracking  
✔ Config-driven event onboarding  
✔ CI/CD bundle deployment  

### Next Enhancements
➡ GitHub Actions automation  
➡ Replay/backfill framework  
➡ Observability dashboards  

---

## 👨‍💻 Author

Ashraf Syed  
Senior Data Engineering Portfolio Project  
Streaming Data Cleaning Platform Initiative
```

---

