---

# ✅ Project 01 – README.md

*(Clean, Senior-Level Version)*

---

# Project 01 — Multi-Tenant Streaming Platform on Azure

⬅️ Back to the platform overview: [Repo README](../../README.md)

Production-style streaming data platform built using Azure Event Hub, Databricks Structured Streaming, Delta Lake, and config-driven multi-tenant architecture.

This project demonstrates how to build a reusable streaming engine where new clients and event types can be onboarded **without modifying core pipeline logic**.

---

## 🎯 What This Project Proves

* Production-grade streaming architecture
* Multi-tenant isolation using configuration
* Schema validation and contract-first ingestion
* DLQ handling for corrupt events
* Observability with audit tracking
* CI/CD deployment using Databricks Asset Bundles
* Environment promotion (dev → stage → prod)

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

All data is stored in Delta Lake using Medallion architecture.

Partitioning strategy:

```
tenant_id / event_type / ingest_date
```

---

## 🧱 Core Components Implemented

### 1️⃣ Bronze Layer

* Structured Streaming ingestion from Event Hub
* Universal envelope parsing
* Corrupt JSON detection
* Dead Letter Queue routing
* Raw Delta writes

**Files:**

```
bundles/streaming_platform/src/bronze/
```

---

### 2️⃣ Silver Layer

* Schema validation (event-type specific)
* Data quality rule enforcement
* Standardization and enrichment
* Clean Delta tables

**Files:**

```
bundles/streaming_platform/src/silver/
```

---

### 3️⃣ Gold Layer

* Device-level aggregations
* Merge/upsert logic
* Analytics-ready serving tables

**Files:**

```
bundles/streaming_platform/src/gold/
```

---

## 🧩 Multi-Tenant Architecture

Tenant isolation implemented through:

* `tenant_id` in universal event envelope
* Tenant-specific configuration files
* Partitioned Delta storage
* Environment-based config overrides

New tenants require only configuration changes.

No pipeline rewrite required.

---

## 📦 Universal Event Envelope (Contract-First Design)

All events follow a standard structure:

* tenant_id
* site_id
* device_id
* device_type
* event_type
* event_id
* event_time_utc
* ingest_time_utc
* schema_version
* source_system
* payload
* attributes

This ensures:

* Clean separation of metadata vs payload
* Schema evolution support
* Engine reuse across industries
* Strong validation at Bronze

---

## 📊 Observability & Audit

Each batch records:

* input_rows
* output_rows
* dlq_rows
* processing latency
* job status
* processing duration

Audit table:

```
audit/audit_pipeline_batches
```

This enables operational monitoring and SLA validation.

---

## 🚨 Dead Letter Queue (DLQ)

Invalid or corrupt events are:

* Detected during Bronze parsing
* Routed to DLQ with reason codes
* Stored separately for replay and analysis

This prevents pipeline failure due to bad upstream data.

---

## ⚙️ Config-Driven Onboarding

### Add New Event Type

1. Add schema JSON
2. Add rule YAML
3. Update tenant config

No core logic change.

---

### Add New Tenant

1. Create tenant config folder
2. Add dev / stage / prod YAML
3. Deploy bundle

Core engine remains unchanged.

---

## 🔄 CI/CD & Deployment

Implemented:

* Databricks Asset Bundles
* Multi-environment targets
* Parameterized jobs
* Structured job orchestration (Bronze → Silver → Gold)

Workflows located in:

```
.github/workflows/
```

Bundle definition:

```
databricks.yml
```

---

## 📸 Production Evidence

Screenshots available in:

## 📸 Proof of Execution (Production Evidence)

All screenshots are stored in: `docs/screenshots/project01/`

| Evidence | What it Shows |
|---------|----------------|
| ✅ Job Orchestration (Bronze → Silver → Gold) | Successful multi-task job run end-to-end |
| ✅ Config-Driven Execution | YAML override enabling event version change without code changes |
| ✅ DLQ Isolation | Corrupt/invalid JSON routed safely without breaking the pipeline |
| ✅ Audit Metrics | Batch-level metrics: input/output rows, DLQ rows, latency, job status |
| ✅ Gold Output | Aggregated serving output written to Gold tables |

### 1) Job Orchestration (Bronze → Silver → Gold)
![Databricks Job Success](../../docs/screenshots/project01/01-job-success.png)

### 2) Config-Driven Execution (Event Version Override)
![Config Override](../../docs/screenshots/project01/02-runner-config-v2.png)

### 3) DLQ – Corrupt Event Isolation
![DLQ Table](../../docs/screenshots/project01/03-dlq-table.png)

### 4) Observability – Audit Metrics
![Audit Metrics](../../docs/screenshots/project01/04-audit-dlq-count.png)

### 5) Gold Layer Output (Serving Tables)
![Gold Output](../../docs/screenshots/project01/05-gold-output.png)

Includes:

* Job success runs
* Config override proof
* DLQ isolation
* Audit metrics tracking
* Gold output tables

---

## 🚀 Runtime Modes

POC Mode:

```
run_minutes = 5
```

Production Mode:

```
run_minutes = 0
```

Enables controlled demonstration during interviews.

---

## 🧠 Design Decisions

| Decision               | Reason                               |
| ---------------------- | ------------------------------------ |
| Universal Envelope     | Reusability + contract enforcement   |
| Medallion Architecture | Clear separation of responsibilities |
| Config-Driven Tenants  | Scalability without code rewrite     |
| Delta Lake             | ACID compliance + streaming support  |
| Audit Table            | Operational transparency             |
| DLQ Isolation          | Fault tolerance                      |

---

## 📌 Why This Matters

This project demonstrates:

* Senior-level architectural thinking
* Platform-first design
* Real-world multi-client scalability
* DevOps maturity
* Business-ready streaming foundation

It is designed to scale into:

* IoT streaming
* RFID tracking
* Industrial telemetry
* Data cleaning services
* Event-driven AI pipelines

---

## 👨‍💻 Author

Ashraf Syed

Senior Data Engineering Portfolio

Azure Streaming Platform Initiative

---
⬅️ Back to the platform overview: [Repo README](../../README.md)
---


