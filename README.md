# 80/20 Reusable Streaming Platform (Azure + Databricks)

A reusable, production-style streaming data platform built on Azure and Databricks.

This repository represents a **config-driven, multi-tenant streaming engine** where:

* **80% is reusable platform infrastructure**
* **20% is configuration per client and per event type**

The goal is to enable fast onboarding of new clients and new streaming event types without modifying core pipeline code.

---

## 🎯 Purpose

This platform is designed for:

* Senior-level data engineering portfolio demonstration
* Multi-tenant streaming architecture pattern
* Real-world DevOps + CI/CD implementation
* A foundation for a streaming data cleaning business

---

## 🏗 Core Architecture

Event Hub → Bronze → Silver → Gold (Delta Lake)

All storage follows Medallion architecture in ADLS Gen2.

Partition strategy:

```
tenant_id / event_type / ingest_date
```

This enables:

* Tenant isolation
* Efficient querying
* Backfill and replay support
* Clean cost control

---

## 🧱 Technology Stack

| Layer               | Technology                              |
| ------------------- | --------------------------------------- |
| Streaming Ingestion | Azure Event Hub                         |
| Processing          | Azure Databricks (Structured Streaming) |
| Storage             | Azure Data Lake Storage Gen2            |
| Table Format        | Delta Lake                              |
| Orchestration       | Databricks Multi-Task Jobs              |
| CI/CD               | Databricks Asset Bundles                |
| Identity            | Managed Identity                        |

---

## 🧩 80% Reusable Platform Engine

```
src/
  common/
  bronze/
  silver/
  gold/
```

### src/common

* Configuration loader
* Logging utilities
* Envelope validation
* Audit tracking

### src/bronze

* Event Hub ingestion
* Envelope parsing
* DLQ routing
* Bronze Delta writes

### src/silver

* Schema validation
* Data quality enforcement
* Standardization & enrichment

### src/gold

* Aggregations
* Serving tables
* Analytics-ready datasets

This engine does not change per client.

---

## ⚙ 20% Configurable Surface

```
configs/
  global/
  tenants/

schemas/
  event_types/

rules/
  event_types/
```

### configs/tenants

Per-tenant environment configs (dev / stage / prod)

### schemas/event_types

Payload schema definitions per event type

### rules/event_types

Data quality validation rules per event type

New clients and new event types are onboarded via configuration only.

---

## 📦 Universal Event Envelope

All streaming events follow a standardized contract:

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

* Multi-client support
* Schema evolution
* Platform reuse
* Clean separation of payload vs metadata

---

## 🚀 Onboarding Model

### Add New Event Type

1. Add schema file
2. Add rule file
3. Update tenant config

No core pipeline rewrite required.

### Add New Client

1. Create tenant folder
2. Add environment configs
3. Deploy bundle

Platform remains unchanged.

---

## 📊 Observability

Audit metrics track:

* input_rows
* output_rows
* dlq_rows
* processing latency
* job status

Audit table:

```
audit/audit_pipeline_batches
```

---

## 🔄 CI/CD

Implemented:

* Databricks Asset Bundles
* Multi-environment targets
* Parameterized jobs

Planned:

* GitHub Actions automation

---

## 📂 Documentation

Located in:

```
docs/
```

Includes:

* Runbook
* Client onboarding guide
* Event onboarding guide
* Platform context documentation

---

## 📁 Projects in This Repository

* Project 01 – Streaming Platform Implementation (Azure + Databricks)
## 📁 Portfolio Projects

- [Project 01 — Multi-Tenant Streaming Platform on Azure](projects/project-01/README.md)
Each project has its own README with deployment details and proof of execution.

---

## 👨‍💻 Author

Ashraf Syed

Senior Data Engineering Portfolio

Streaming Data Platform Initiative

---




