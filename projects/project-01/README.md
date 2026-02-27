
# Project 01 — Multi-Tenant Streaming Platform on Azure

⬅️ Back to the platform overview: [Repo README](../../README.md)

A production-style, multi-tenant streaming data platform built using:

- Azure Event Hub  
- Azure Databricks (Structured Streaming)  
- Delta Lake  
- Config-driven architecture  

This project demonstrates a reusable streaming engine where new tenants and event types can be onboarded **without modifying core pipeline logic**.

---

## 🎯 What This Project Demonstrates

- Production-grade streaming architecture
- Multi-tenant isolation via configuration
- Contract-first ingestion (Universal Event Envelope v2)
- DLQ isolation for corrupt or invalid events
- Observability with batch-level audit tracking
- CI/CD deployment using Databricks Asset Bundles
- Deterministic runtime control via job parameter

This is not a demo notebook — it is a deployable streaming platform.

---

## 🏗 End-to-End Architecture

```

Azure Event Hub
↓
Bronze (Envelope + DLQ)
↓
Silver (Schema + Data Quality)
↓
Gold (Curated + Metrics)

```

All data is stored in Delta Lake following Medallion architecture.

### Partition Strategy

```

tenant_id / event_type / ingest_date

```

This enables:

- Tenant isolation  
- Efficient queries  
- Replay & backfill  
- Clean cost management  

---

## 🧱 Core Components

### 1️⃣ Bronze Layer

- Structured Streaming ingestion from Event Hub
- Universal envelope (v2) standardization
- Corrupt JSON detection
- DLQ routing with reason codes
- Delta writes partitioned by tenant/event/date

**Source Code**
```

bundles/streaming_platform/src/bronze/

```

---

### 2️⃣ Silver Layer

- Event-type schema validation
- Data quality rule enforcement
- Standardization & enrichment
- Cleaned Delta tables

**Source Code**
```

bundles/streaming_platform/src/silver/

```

---

### 3️⃣ Gold Layer

- Aggregations (hour/day grain)
- Merge/upsert logic
- Analytics-ready serving tables


# Project 01 — Multi-Tenant Streaming Platform on Azure

⬅️ Back to the platform overview: [Repo README](../../README.md)

Production-style streaming data platform built using Azure Event Hub, Databricks Structured Streaming, Delta Lake, and config-driven multi-tenant architecture.

This project demonstrates how to build a reusable streaming engine where new clients and event types can be onboarded **without modifying core pipeline logic**.

---

## 🎯 What This Project Proves

- Production-grade streaming architecture  
- Multi-tenant isolation using configuration  
- Schema validation and contract-first ingestion  
- Dead Letter Queue (DLQ) handling  
- Observability with audit tracking  
- CI/CD deployment using Databricks Asset Bundles  
- Environment promotion (dev → stage → prod)  

This is not a demo notebook — this is a deployable platform.

---

## 🏗 End-to-End Architecture

```
Azure Event Hub
        ↓
Bronze (Raw + Envelope Validation)
        ↓
Silver (Schema + Data Quality Enforcement)
        ↓
Gold (Aggregations + Serving Tables)
```

All data is stored in **Delta Lake** using Medallion architecture.

Partition strategy:

```
tenant_id / event_type / ingest_date
```

---

## 🧱 Core Components

### 1️⃣ Bronze Layer (Delta)

- Structured Streaming ingestion from Event Hub  
- Universal envelope parsing  
- Corrupt JSON detection  
- Dead Letter Queue routing  
- Raw Delta writes  

---

### 2️⃣ Silver Layer (Delta)

- Event-type schema validation  
- Data quality rule enforcement  
- Standardization and enrichment  
- Clean Delta tables  

---

### 3️⃣ Gold Layer (Delta Serving Layer)

The Gold layer provides analytics-ready datasets.

All Gold outputs are stored as **Delta Lake tables**.

#### Gold Tables

- `/gold_curated`
- `/gold_metrics`

Partitioned by:

```
tenant_id / event_type / ingest_date
```

This ensures:

- Efficient filtering  
- Multi-tenant isolation  
- Replay and backfill safety  
- ACID-compliant incremental processing  

---

## 📈 Time-Series Analytics Support

Gold metrics include time-bucketed aggregations suitable for trend analysis and BI tools such as Power BI.

Example metrics:

- Average temperature  
- Minimum / maximum temperature  
- Average humidity  
- Event count per time window  

Example query:

```sql
SELECT
  event_time_bucket,
  avg_temperature_f,
  avg_humidity_pct,
  event_count
FROM delta.`/Volumes/platform/dev/streaming_platform/env=dev/gold_metrics`
WHERE tenant_id = 'tenant_demo'
ORDER BY event_time_bucket ASC;
```

---

## 📊 Observability & Audit

Each batch records:

- input_rows  
- output_rows  
- dlq_rows  
- processing latency  
- job status  
- processing duration  

Audit table:

```
audit/audit_pipeline_batches
```

This enables operational monitoring and SLA validation.

---

## 🚨 Dead Letter Queue (DLQ)

Invalid or corrupt events are:

- Detected during Bronze parsing  
- Routed to DLQ with reason codes  
- Stored separately for replay and analysis  

This prevents pipeline failure due to bad upstream data.

---

## ⚙️ Config-Driven Onboarding

### Add New Event Type

1. Add schema file  
2. Add rule file  
3. Update tenant config  

No core logic change required.

### Add New Tenant

1. Create tenant config folder  
2. Add environment YAML files  
3. Deploy bundle  

The engine remains unchanged.

---

## ▶️ How to Run Project 01

### Deploy

```bash
databricks bundle deploy -t dev
```

### Execute

```bash
databricks bundle run -t dev streaming_platform_job
```

Or use GitHub Actions:

1. Navigate to **Actions**
2. Select **CD - Deploy Dev Bundle**
3. Click **Run workflow**
4. Set `run_job = true`

---

## 🔍 Verify Gold is Delta

```sql
DESCRIBE DETAIL delta.`/Volumes/platform/dev/streaming_platform/env=dev/gold_metrics`;
```

Presence of `_delta_log` confirms Delta format.

---

## 🧠 Design Decisions

| Decision | Reason |
|----------|--------|
| Universal Event Envelope | Reusability + contract enforcement |
| Medallion Architecture | Clear separation of responsibilities |
| Config-Driven Tenants | Scalability without code rewrite |
| Delta Lake | ACID compliance + streaming support |
| Audit Table | Operational transparency |
| DLQ Isolation | Fault tolerance |

---
---

**Source Code**
```

bundles/streaming_platform/src/gold/

```

---

## 🧩 Multi-Tenant Design

Tenant isolation is achieved through:

- `tenant_id` in the universal envelope
- Tenant-specific configuration files
- Partitioned Delta storage
- Environment-based config promotion (dev → stage → prod)

New tenants require configuration only — no pipeline rewrite.

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

This ensures:

- Clean separation of metadata vs payload
- Schema evolution support
- Multi-industry reuse
- Strong validation boundaries

---

## 📊 Observability & Audit

Each streaming batch records:

- input_rows  
- output_rows  
- dlq_rows  
- batch status  
- processing timestamps  

Audit table location:

```

audit/audit_pipeline_batches

```

This enables operational transparency and SLA validation.

---

## ⏱ Deterministic Runtime Control

Project 01 supports controlled runtime execution via a single job parameter:

```

run_minutes

```

- Passed from GitHub workflow input
- Applied consistently across Bronze → Silver → Gold
- Not controlled by tenant YAML

### Example Runs

| Scenario      | run_minutes |
|--------------|------------|
| Smoke Test    | 1          |
| Demo Run      | 5          |
| Extended Test | 30         |

This ensures predictable demonstrations during interviews.

---

## 🔄 CI/CD & Deployment

Implemented:

- Databricks Asset Bundles
- Multi-environment targets
- Parameterized multi-task job orchestration
- GitHub Actions manual deployment

Key files:

```

databricks.yml
.github/workflows/

```

---

## 📸 Proof of Execution

Screenshots located in:

```

docs/screenshots/project01/

```

| Evidence | Description |
|----------|-------------|
| Job Orchestration | Bronze → Silver → Gold successful run |
| Config Override | Event version change without code modification |
| DLQ Isolation | Corrupt event safely routed |
| Audit Metrics | Batch metrics recorded |
| Gold Output | Aggregated serving tables |

### Job Orchestration
![Job Success](../../docs/screenshots/project01/01-job-success.png)

### Config-Driven Execution
![Config Override](../../docs/screenshots/project01/02-runner-config-v2.png)

### DLQ Isolation
![DLQ Table](../../docs/screenshots/project01/03-dlq-table.png)

### Audit Metrics
![Audit Metrics](../../docs/screenshots/project01/04-audit-dlq-count.png)

### Gold Output
![Gold Output](../../docs/screenshots/project01/05-gold-output.png)

---

## 🧠 Key Design Decisions

| Decision | Reason |
|----------|--------|
| Universal Envelope | Reusability + contract enforcement |
| Medallion Architecture | Separation of responsibilities |
| Config-Driven Tenants | Scalability without code rewrite |
| Delta Lake | ACID guarantees + streaming compatibility |
| Audit Table | Operational visibility |
| DLQ Isolation | Fault tolerance |

---

## 📌 Why This Matters

This project demonstrates:

- Senior-level architectural thinking
- Platform-first mindset
- Real-world multi-client scalability
- DevOps maturity
- A production-ready streaming foundation

It is designed to scale into:

- IoT streaming
- RFID tracking
- Industrial telemetry
- Event-driven AI pipelines
- Data cleaning services

---

## 👨‍💻 Author

**Ashraf Syed**  
Senior Data Engineering Portfolio  
Azure Streaming Platform Initiative  

⬅️ Back to the platform overview: [Repo README](../../README.md)

```




