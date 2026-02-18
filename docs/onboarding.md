# Streaming Platform – Onboarding Guide

This guide explains how to onboard:

1. A new event type
2. A new sensor
3. A new client (tenant)

The platform follows the 80/20 principle:

- 80% reusable core
- 20% configurable per client/event

---

# 1. Onboard a New Event Type (Same Client)

## Step 1 – Update Tenant Config

Edit:

configs/tenants/<tenant_id>/dev.yml


Add event type:

events:
allowed_event_types:
- temp_humidity.v2

## Step 2 – Add Schema

Create:

schemas/event_types/<event_type>.json


Define JSON structure for payload.

## Step 3 – Add Validation Rules (Optional)

Create:

rules/event_types/<event_type>.yml


Example:

required_fields:

device_id

timestamp_utc


## Step 4 – Update Silver Transform

Modify Silver notebook logic for new event_type if transformation differs.

No Bronze rewrite required.

---

# 2. Onboard a New Sensor (Same Client)

If schema changes:

1. Add new event_type version
2. Add schema file
3. Add validation rules
4. Update Silver transformation logic

Keep old event_type active if backward compatibility required.

---

# 3. Onboard a New Client (Non-Franchise)

## Step 1 – Create Tenant Folder

configs/tenants/<new_tenant>/


Add:

- dev.yml
- stage.yml
- prod.yml

## Step 2 – Define Base Storage

Inside YAML:

storage:
base_path: abfss://.../platform


Partitioning:

tenant_id / event_type / ingest_date


No code changes required.

---

# 4. Multi-Client Isolation

Each record contains:

- tenant_id
- site_id
- event_type

Data is partitioned by:

tenant_id / event_type / ingest_date


This ensures:

- Logical isolation
- Query performance
- Scalability

---

# 5. Franchise Model (Future – Level 2)

In franchise mode:

- Core 80% platform is protected
- Franchise users edit only:
  - YAML configs
  - schemas
  - rule files

Core logic remains internal.

(Not implemented in Project 01.)

---

# 6. Promotion Across Environments

Use bundle targets:

databricks bundle deploy -t stage
databricks bundle deploy -t prod


Each environment uses separate:

- run_minutes
- config files
- workspace host

---

# 7. Checklist

Before running:

- Schema exists
- Rules exist
- Config updated
- Event Hub publishing correct event_type
- run_minutes set correctly

---

End of Onboarding Guide.

