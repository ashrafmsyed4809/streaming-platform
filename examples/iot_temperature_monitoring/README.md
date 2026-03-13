# Example: IoT Temperature & Humidity Monitoring

This directory demonstrates how the streaming platform can be used to process
IoT sensor telemetry from Raspberry Pi devices.

The example uses a **temperature and humidity sensor (SHT4x)** connected to a
Raspberry Pi that continuously sends telemetry events to Azure Event Hub.

The platform processes these events using the reusable streaming engine.

## Event Flow

Raspberry Pi Sensor
→ Azure Event Hub
→ Bronze
→ Silver
→ Data Quality Engine
→ Gold Curated Tables
→ Gold Metrics


## Event Schema

Event type:

temp_humidity.v2

Fields:

| Field | Description |
|------|-------------|
device_id | Unique sensor device identifier |
event_time_utc | Timestamp of sensor reading |
temperature_f | Temperature in Fahrenheit |
humidity_pct | Relative humidity percentage |
battery_pct | Device battery level |
firmware_version | Sensor firmware version |
sensor | Sensor model |
serial_number | Sensor hardware serial |

## Example Use Cases

This architecture can support:

- Cold storage temperature monitoring
- HVAC environmental monitoring
- Smart building telemetry
- Industrial IoT sensor streams
- Environmental monitoring networks

The example demonstrates how a **single reusable streaming platform can support multiple industries through configuration-driven onboarding.**