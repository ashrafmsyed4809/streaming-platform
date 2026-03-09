
# Project 03 — Schema Evolution Handling

## Overview

Project 03 demonstrates how the streaming platform handles **schema evolution** for an existing event type without breaking the pipeline.

The original sensor event contract was:

```
temp_humidity.v1
```

This project introduces a **new version of the same event type**:

```
temp_humidity.v2
```

The platform processes **both versions simultaneously** while maintaining backward compatibility.

This mirrors real-world production scenarios where device firmware upgrades introduce new fields or rename existing ones.

---

# Goal of Project 03

Demonstrate that the platform can:

* process **multiple schema versions** of the same event type
* support **backward compatibility**
* evolve event contracts without breaking downstream pipelines
* automatically evolve the Silver table schema

---

# Architecture

The core architecture of the platform remains unchanged.

```
Azure Event Hub
      ↓
Bronze (Universal Envelope + DLQ)
      ↓
Silver (Validation + Standardization)
      ↓
Gold (Curated + Metrics)
```

Schema evolution is handled primarily at the **Silver layer**.

---

# Event Schema Evolution

## Version 1 (Original)

Example payload:

```json
{
  "event_type": "temp_humidity.v1",
  "device_id": "pi-003",
  "timestamp_utc": "2026-03-08 05:00:01",
  "temperature_f": 73.1,
  "humidity_pct": 67.4,
  "sensor": "SHT4x",
  "serial_number": "0x105d909c"
}
```

Fields:

```
device_id
timestamp_utc
temperature_f
humidity_pct
sensor
serial_number
```

---

## Version 2 (New)

Example payload:

```json
{
  "event_type": "temp_humidity.v2",
  "device_id": "pi-004",
  "event_time_utc": "2026-03-08 05:00:05",
  "temperature_f": 73.3,
  "humidity_pct": 67.1,
  "battery_pct": 91.0,
  "firmware_version": "2.1.0",
  "sensor": "SHT4x",
  "serial_number": "0x105d909c"
}
```

Changes introduced:

| Change        | Description                        |
| ------------- | ---------------------------------- |
| renamed field | `timestamp_utc` → `event_time_utc` |
| new field     | `battery_pct`                      |
| new field     | `firmware_version`                 |

---

# Contract-Driven Schema Validation

Each event version has its own **contract definition**.

```
configs/contracts/temp_humidity.v1.yml
configs/contracts/temp_humidity.v2.yml
```

Example contract:

```yaml
fields:
  - name: device_id
    type: string
    nullable: false

  - name: event_time_utc
    type: timestamp
    nullable: false

  - name: temperature_f
    type: double
    nullable: true

  - name: humidity_pct
    type: double
    nullable: true

  - name: battery_pct
    type: double
    nullable: true

  - name: firmware_version
    type: string
    nullable: true

  - name: sensor
    type: string
    nullable: true

  - name: serial_number
    type: string
    nullable: true
```

The Silver collector dynamically loads these contracts to build a Spark schema.

---

# Key Platform Change

To support evolving schemas, the Silver write operation enables **Delta schema evolution**.

```python
.option("mergeSchema", "true")
```

This allows new fields introduced by later event versions to be added to the Silver table without breaking the pipeline.

---

# Test Setup

Two Raspberry Pi sender scripts simulate different device firmware versions.

```
temp_humidity_v1_sender.py
temp_humidity_v2_sender.py
```

Both scripts send events simultaneously to the same Event Hub stream.

This simulates a real-world upgrade scenario where:

* older devices continue sending `v1`
* upgraded devices send `v2`

---

# Validation Results

Gold validation confirms both versions were successfully processed.

```
curated rows
temp_humidity.v1 : 28
temp_humidity.v2 : 139
```

Example validation output:

```
+----------------+-----+
|event_type      |count|
+----------------+-----+
|temp_humidity.v1|28   |
|temp_humidity.v2|139  |
+----------------+-----+
```

Both versions appear in the curated dataset.

---

# Key Lessons

Project 03 highlights several real-world streaming challenges:

* schema changes from device firmware upgrades
* maintaining backward compatibility
* evolving table schemas safely
* contract-driven validation
* replaying historical events after schema fixes

These capabilities are critical for production streaming systems where upstream producers evolve independently of downstream consumers.

---

# Outcome

The platform now supports:

* **multiple schema versions**
* **contract-based validation**
* **Delta schema evolution**
* **mixed-version event processing**

This completes the **schema evolution capability** of the streaming platform.

---

