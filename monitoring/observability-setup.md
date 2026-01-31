# Observability Setup for Panelin API

This guide covers logging, metrics, tracing, and dashboards for the Panelin API.

## Table of Contents

1. [Structured Logging](#structured-logging)
2. [Cloud Trace Integration](#cloud-trace-integration)
3. [Custom Metrics](#custom-metrics)
4. [Dashboard Setup](#dashboard-setup)
5. [SLO Configuration](#slo-configuration)

---

## Structured Logging

### Configure Structured Logging in FastAPI

Add to your `api.py`:

```python
import os
import json
import logging
from datetime import datetime

# Configure structured logging for Cloud Logging
class CloudLoggingFormatter(logging.Formatter):
    """Format logs as JSON for Cloud Logging."""
    
    def format(self, record):
        log_entry = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "logging.googleapis.com/sourceLocation": {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName
            }
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add custom fields
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
            
        return json.dumps(log_entry)

# Setup logging
def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(CloudLoggingFormatter())
    
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    
    return root

logger = setup_logging()
```

### Using google-cloud-logging

Alternative using the official library:

```python
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler

def setup_cloud_logging():
    client = google.cloud.logging.Client()
    handler = CloudLoggingHandler(client)
    
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)
```

### Log Levels & When to Use

| Level | Use Case | Example |
|-------|----------|---------|
| DEBUG | Development debugging | `logger.debug(f"Calculating quote for {product_id}")` |
| INFO | Normal operations | `logger.info(f"Quote created: {quote_id}")` |
| WARNING | Unexpected but handled | `logger.warning(f"Slow API response: {latency}ms")` |
| ERROR | Errors requiring attention | `logger.error(f"Failed to fetch product: {e}")` |
| CRITICAL | System failures | `logger.critical("Database connection lost")` |

---

## Cloud Trace Integration

### Install Dependencies

```bash
pip install opentelemetry-api opentelemetry-sdk \
    opentelemetry-exporter-gcp-trace \
    opentelemetry-instrumentation-fastapi \
    opentelemetry-instrumentation-requests
```

### Configure Tracing

Create `tracing.py`:

```python
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

def setup_tracing(app):
    """Configure OpenTelemetry tracing for Cloud Trace."""
    
    # Only enable in production
    if os.getenv("ENVIRONMENT") != "production":
        return
    
    # Set up the tracer provider
    provider = TracerProvider()
    
    # Configure Cloud Trace exporter
    exporter = CloudTraceSpanExporter()
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    
    # Set the global tracer provider
    trace.set_tracer_provider(provider)
    
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    
    # Instrument outgoing HTTP requests
    RequestsInstrumentor().instrument()
    
    return trace.get_tracer(__name__)
```

### Use in Application

```python
from tracing import setup_tracing

app = FastAPI(...)
tracer = setup_tracing(app)

@app.post("/quotes")
async def create_quote(request: QuoteRequest):
    with tracer.start_as_current_span("calculate_quote") as span:
        span.set_attribute("product_id", request.product_id)
        span.set_attribute("length_m", request.length_m)
        
        # Your business logic
        result = calculate_panel_quote(...)
        
        span.set_attribute("total_price", result.total_price)
        return result
```

---

## Custom Metrics

### Using Prometheus Client

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# Define metrics
REQUEST_COUNT = Counter(
    'panelin_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'panelin_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

QUOTE_TOTAL = Counter(
    'panelin_quotes_total',
    'Total quotes generated',
    ['product_family']
)

QUOTE_VALUE = Histogram(
    'panelin_quote_value_usd',
    'Quote values in USD',
    buckets=[100, 500, 1000, 5000, 10000, 50000]
)

ACTIVE_CONNECTIONS = Gauge(
    'panelin_active_connections',
    'Current active connections'
)

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### Middleware for Automatic Metrics

```python
import time
from starlette.middleware.base import BaseHTTPMiddleware

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        
        ACTIVE_CONNECTIONS.inc()
        
        try:
            response = await call_next(request)
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(time.time() - start_time)
            
            return response
        finally:
            ACTIVE_CONNECTIONS.dec()

app.add_middleware(MetricsMiddleware)
```

---

## Dashboard Setup

### Create Dashboard via gcloud

```bash
gcloud monitoring dashboards create --config-from-file=dashboard.json
```

### Dashboard Configuration (dashboard.json)

```json
{
  "displayName": "Panelin API Dashboard",
  "gridLayout": {
    "columns": "2",
    "widgets": [
      {
        "title": "Request Rate",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"panelin-api\" AND metric.type=\"run.googleapis.com/request_count\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_RATE"
                }
              }
            }
          }]
        }
      },
      {
        "title": "Latency (P50, P95, P99)",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"panelin-api\" AND metric.type=\"run.googleapis.com/request_latencies\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_PERCENTILE_50"
                }
              }
            },
            "legendTemplate": "P50"
          },
          {
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"panelin-api\" AND metric.type=\"run.googleapis.com/request_latencies\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_PERCENTILE_95"
                }
              }
            },
            "legendTemplate": "P95"
          }]
        }
      },
      {
        "title": "Error Rate",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"panelin-api\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"5xx\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_RATE"
                }
              }
            }
          }]
        }
      },
      {
        "title": "Instance Count",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"panelin-api\" AND metric.type=\"run.googleapis.com/container/instance_count\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_MAX"
                }
              }
            }
          }]
        }
      },
      {
        "title": "CPU Utilization",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"panelin-api\" AND metric.type=\"run.googleapis.com/container/cpu/utilizations\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_PERCENTILE_95"
                }
              }
            }
          }]
        }
      },
      {
        "title": "Memory Utilization",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"panelin-api\" AND metric.type=\"run.googleapis.com/container/memory/utilizations\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_PERCENTILE_95"
                }
              }
            }
          }]
        }
      }
    ]
  }
}
```

---

## SLO Configuration

### Define SLOs

| Metric | Target | Window |
|--------|--------|--------|
| Availability | 99.9% | 30 days |
| Latency (P95) | < 500ms | 30 days |
| Error Rate | < 0.1% | 30 days |

### Create SLO via gcloud

```bash
# Create availability SLO
gcloud slo create panelin-api-availability \
  --display-name="Panelin API Availability" \
  --goal=0.999 \
  --rolling-period-days=30 \
  --request-based-sli \
  --good-total-ratio-threshold \
  --good-service-filter='resource.type="cloud_run_revision" AND metric.labels.response_code_class!="5xx"' \
  --total-service-filter='resource.type="cloud_run_revision"'
```

### Error Budget Alerts

```yaml
# Add to alert-policies.yaml
---
displayName: "Panelin API - SLO Error Budget Burn Rate"
documentation:
  content: |
    ## Error Budget Alert
    
    The error budget is being consumed faster than expected.
    Current burn rate exceeds threshold.
    
    ### Actions:
    1. Investigate recent changes
    2. Consider rollback if issue is deployment-related
    3. Check dependency health
combiner: OR
conditions:
  - displayName: "Error budget burn rate > 1"
    conditionThreshold:
      filter: |
        select_slo_burn_rate("projects/PROJECT_ID/services/panelin-api/serviceLevelObjectives/availability-slo", "1h")
      comparison: COMPARISON_GT
      thresholdValue: 1
      duration: 0s
```

---

## Quick Commands

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=panelin-api" --limit=100

# View error logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=panelin-api AND severity>=ERROR" --limit=50

# View traces
gcloud trace spans list --limit=50

# Check current metrics
gcloud monitoring metrics-scopes describe projects/YOUR_PROJECT

# List alert policies
gcloud alpha monitoring policies list --filter="displayName:panelin"
```
