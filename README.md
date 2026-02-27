
# 80/20 Reusable Streaming Platform (Azure + Databricks)

A reusable, production-style, multi-tenant streaming data platform built on Azure and Databricks.

This repository demonstrates a **config-driven streaming engine** where:

- **80% is reusable platform infrastructure**
- **20% is configuration per client and per event type**

The objective is to onboard new clients and new streaming event types without modifying core pipeline code.

---

## 🎯 Purpose

This platform demonstrates:

- Senior-level streaming architecture
- Multi-tenant data isolation
- Structured Streaming best practices
- Deterministic runtime control
- DevOps & CI/CD using Databricks Asset Bundles
- Production-style observability & audit tracking

It serves as both:
- A portfolio demonstration
- A foundation for a scalable streaming data platform

---

## 🏗 Core Architecture

```

Azure Event Hub
↓
Bronze (Envelope + DLQ)
↓
Silver (Validation + Standardization)
↓
Gold (Curated + Metrics)

```

Storage follows **Medallion Architecture** in ADLS Gen2 using Delta Lake.

### Partition Strategy

```

tenant_id / event_type / ingest_date

```

This enables:

- Tenant isolation
- Efficient querying
- Replay & backfill
- Cost control
- Clean operational boundaries

---

## 🧱 Technology Stack

| Layer               | Technology                              |
|---------------------|-----------------------------------------|
| Streaming Ingestion| Azure Event Hub                         |
| Processing         | Azure Databricks (Structured Streaming) |
| Storage            | Azure Data Lake Storage Gen2            |
| Table Format       | Delta Lake                              |
| Orchestration      | Databricks Multi-Task Jobs              |
| CI/CD              | Databricks Asset Bundles + GitHub Actions |
| Identity           | Managed Identity                        |

---

## 🧩 80% Reusable Platform Engine

```

bundles/streaming_platform/src/
bronze/
silver/
gold/
common/

```

### Bronze
- Event Hub ingestion
- Universal envelope creation (v2)
- DLQ isolation
- Audit batch tracking

### Silver
- Contract validation
- Data quality enforcement
- Standardization & enrichment

### Gold
- Curated datasets
- Metrics aggregation
- Analytics-ready serving tables

This layer does **not change per client**.

---

## ⚙ 20% Configurable Surface

```

configs/
tenants/

schemas/
event_types/

rules/
event_types/

```

New clients and event types are onboarded **via configuration only**.

### Add New Event Type
1. Add schema definition
2. Add validation rules
3. Update tenant config

### Add New Client
1. Create tenant config
2. Deploy bundle
3. Start ingestion

No pipeline rewrite required.

---

## 📦 Universal Event Envelope (v2)

All events are standardized before leaving Bronze:

- tenant_id  
- site_id  
- device_id  
- event_type  
- event_id  
- event_time_utc  
- ingest_time_utc  
- schema_version  
- source_system  
- payload  
- attributes  

This enables:

- Multi-tenant scalability
- Schema evolution
- Clean metadata separation
- Safe replay & reprocessing

---

## ⏱ Deterministic Runtime Control

Runtime duration is controlled by a **single job parameter**:

```

run_minutes

```

- Passed from GitHub workflow input
- Applied consistently across Bronze → Silver → Gold
- Tenant YAML does NOT control runtime duration

### Example Runs

| Scenario        | run_minutes |
|---------------|------------|
| Smoke test     | 1          |
| Demo run       | 5          |
| Extended test  | 30         |

All layers honor the same value.

---

## 📊 Observability

Batch-level audit metrics are stored in:

```

audit/audit_pipeline_batches

```

Tracked metrics include:

- input_rows
- output_rows
- dlq_rows
- batch status
- processing timestamps

This enables production-style monitoring and validation.

---

## 🔄 CI/CD

- Databricks Asset Bundles
- Multi-environment targets (dev/stage/prod)
- GitHub Actions manual deployment
- Parameterized job execution


---

▶️ How to Deploy & Run
---
1️⃣ Validate Bundle
---
databricks bundle validate -t dev

2️⃣ Deploy to Databricks Workspace
---

databricks bundle deploy -t dev

This deploys:

Multi-task job (Bronze → Silver → Gold)

Notebooks

Configuration files

Environment-specific overrides

3️⃣ Run the Job
---
databricks bundle run -t dev streaming_platform_job

Or use GitHub Actions:

Go to Actions

Select CD - Deploy Dev Bundle

Click Run workflow

Set run_job = true to execute after deploy

Runtime Modes

Controlled via YAML configuration:

runtime:
  run_minutes: 5   # POC mode (auto-stop after N minutes)

Production mode:

runtime:
  run_minutes: 0   # Continuous execution
Delta Storage Confirmation

All layers use Delta Lake:

Bronze → Delta

Silver → Delta

Gold → Delta (Curated + Metrics)

Audit → Delta

DLQ → Delta

---

## 📁 Portfolio Projects

- [Project 01 — Multi-Tenant Streaming Platform on Azure](projects/project-01/README.md)

Each project contains:
- Architecture details
- Execution proof
- Screenshots
- Deployment steps

---

## 👨‍💻 Author

**Ashraf Syed**  
Senior Data Engineering Portfolio  
Streaming Data Platform Initiative

```



