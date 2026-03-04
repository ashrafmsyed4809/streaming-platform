

# 80/20 Reusable Streaming Platform (Azure + Databricks)

A reusable, production-style **multi-tenant streaming data platform** built on **Azure Event Hub, Azure Databricks, and Delta Lake**.

This repository demonstrates a **config-driven streaming engine** where:

- **80% is reusable platform infrastructure**
- **20% is configuration per client and per event type**

The objective is to **onboard new clients and new streaming event types without modifying core pipeline code**.



# 🎯 Purpose

This platform demonstrates:

- Senior-level **streaming architecture**
- **Multi-tenant data isolation**
- **Structured Streaming best practices**
- **Deterministic runtime control**
- **DevOps & CI/CD using Databricks Asset Bundles**
- **Production-style observability & audit tracking**

It serves as both:

- A **portfolio demonstration**
- A **foundation for a scalable streaming data platform**

---

# 🏗 Platform Architecture


```
Azure Event Hub
↓
Bronze (Envelope + DLQ)
↓
Silver (Validation + Standardization)
↓
Gold (Curated + Metrics)

```

Storage follows **Medallion Architecture** in **ADLS Gen2 using Delta Lake**.

---

# 📦 Version History

| Version | Project | Description |
|-------|--------|-------------|
| v1.0.0 | Project 01 | Streaming Platform Foundation (Bronze → Silver → Gold pipeline) |
| v1.1.0 | Project 02 | Config-Driven Multi-Tenant Onboarding |
| v1.2.0 | Project 03 | Schema Evolution (temp_humidity.v1 → v2) |
| v1.3.0 | Project 04 | Replay / Backfill Capability |
| v1.4.0 | Project 05 | Production Hardening & Observability |

---

# 🧱 Technology Stack

| Layer | Technology |
|------|-------------|
| Streaming Ingestion | Azure Event Hub |
| Processing | Azure Databricks (Structured Streaming) |
| Storage | Azure Data Lake Storage Gen2 |
| Table Format | Delta Lake |
| Orchestration | Databricks Multi-Task Jobs |
| CI/CD | Databricks Asset Bundles + GitHub Actions |
| Identity | Managed Identity |

---

# 🧩 80% Reusable Platform Engine

```

bundles/streaming_platform/src/
├ bronze/
├ silver/
├ gold/
└ common/

```

### Bronze
- Event Hub ingestion
- Universal event envelope creation (v2)
- DLQ isolation
- Audit batch tracking

### Silver
- Contract validation
- Data quality enforcement
- Data standardization and enrichment

### Gold
- Curated datasets
- Metrics aggregation
- Analytics-ready serving tables

This layer **does not change per client**.

---

# ⚙ 20% Configurable Surface

```

configs/
├ tenants/

schemas/
├ event_types/

rules/
├ event_types/

```

New clients and event types are onboarded **via configuration only**.

### Add New Event Type
1. Add schema definition
2. Add validation rules
3. Update tenant configuration

### Add New Client
1. Create tenant configuration
2. Deploy bundle
3. Start ingestion

No pipeline rewrite required.

---

# 📦 Universal Event Envelope (v2)

All events are standardized before leaving Bronze.

Fields include:

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

Benefits:

- Multi-tenant scalability
- Schema evolution support
- Clean metadata separation
- Safe replay & reprocessing

---

# ⏱ Deterministic Runtime Control

Runtime duration is controlled by a **single job parameter**:

```

run_minutes

```

- Passed from GitHub workflow input
- Applied consistently across **Bronze → Silver → Gold**
- Tenant YAML does **not** control runtime duration

### Example Runs

| Scenario | run_minutes |
|--------|------------|
| Smoke Test | 1 |
| Demo Run | 5 |
| Extended Test | 30 |

All layers honor the same runtime configuration.

---

# 📊 Observability

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

This enables **production-style monitoring and validation**.

---

# 🔄 CI/CD

Deployment is managed using:

- **Databricks Asset Bundles**
- **Multi-environment targets (dev / stage / prod)**
- **GitHub Actions deployment workflows**
- **Parameterized job execution**

Example workflow:

```

databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle run -t dev streaming_platform_job

```

GitHub workflow allows:

- selecting deployment target
- controlling runtime duration
- executing smoke tests

---

# ▶️ How to Deploy & Run

### 1️⃣ Validate Bundle

```

databricks bundle validate -t dev



---
```
### 2️⃣ Deploy to Databricks Workspace

```

databricks bundle deploy -t dev

```

This deploys:

- Multi-task job (Bronze → Silver → Gold)
- Notebooks
- Configuration files
- Environment-specific overrides

---

### 3️⃣ Run the Job

```

databricks bundle run -t dev streaming_platform_job

```

Or use **GitHub Actions**:

1. Go to **Actions**
2. Select **CD - Deploy Dev Bundle**
3. Click **Run workflow**
4. Set `run_job = true`

---

# 📁 Repository Structure

```

streaming-platform
│
├ bundles
│   └ streaming_platform
│
├ configs
│   └ tenants
│
├ schemas
│
├ rules
│
├ src
│   ├ bronze
│   ├ silver
│   └ gold
│
├ projects
│   ├ project_01
│   ├ project_02
│   ├ project_03
│   ├ project_04
│   └ project_05
│
└ .github
└ workflows



---
```
# 📁 Portfolio Projects

| Project | Description |
|------|-------------|
| Project 01 | Multi-Tenant Streaming Platform Foundation |
| Project 02 | Config-Driven Tenant Onboarding |
| Project 03 | Schema Evolution Handling |
| Project 04 | Replay / Backfill Capabilities |
| Project 05 | Production Hardening & Observability |

Each project contains:

- architecture explanation
- execution proof
- screenshots
- deployment steps

---

# 👨‍💻 Author

**Ashraf Syed**

Senior Data Engineering Portfolio  
Streaming Data Platform Initiative

---
