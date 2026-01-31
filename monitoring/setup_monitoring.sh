#!/bin/bash
# ============================================================================
# Cloud Monitoring Setup Script
# ============================================================================
# Sets up monitoring dashboards, alerting policies, and notification channels
#
# Usage:
#   export PROJECT_ID=your-project-id
#   export NOTIFICATION_EMAIL=alerts@example.com
#   ./setup_monitoring.sh
# ============================================================================

set -euo pipefail

PROJECT_ID="${PROJECT_ID:-}"
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-panelin-api}"

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------
if [ -z "$PROJECT_ID" ]; then
    log_error "PROJECT_ID is required"
    exit 1
fi

if [ -z "$NOTIFICATION_EMAIL" ]; then
    log_warn "NOTIFICATION_EMAIL not set, skipping notification channel setup"
fi

gcloud config set project "$PROJECT_ID"

# -----------------------------------------------------------------------------
# Enable Monitoring API
# -----------------------------------------------------------------------------
log_info "Enabling Cloud Monitoring API..."
gcloud services enable monitoring.googleapis.com

# -----------------------------------------------------------------------------
# Create Notification Channel (Email)
# -----------------------------------------------------------------------------
if [ -n "$NOTIFICATION_EMAIL" ]; then
    log_info "Creating email notification channel..."
    
    # Check if channel already exists
    EXISTING_CHANNEL=$(gcloud alpha monitoring channels list \
        --filter="displayName='Panelin API Alerts' AND type='email'" \
        --format="value(name)" 2>/dev/null || echo "")
    
    if [ -z "$EXISTING_CHANNEL" ]; then
        gcloud alpha monitoring channels create \
            --display-name="Panelin API Alerts" \
            --type=email \
            --channel-labels=email_address="$NOTIFICATION_EMAIL" \
            --description="Email notifications for Panelin API alerts"
        log_info "Notification channel created for: $NOTIFICATION_EMAIL"
    else
        log_info "Notification channel already exists: $EXISTING_CHANNEL"
    fi
fi

# -----------------------------------------------------------------------------
# Create Uptime Check
# -----------------------------------------------------------------------------
log_info "Creating uptime check..."

# Get Cloud Run URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    # Create uptime check config
    cat > /tmp/uptime-check.json << EOF
{
    "displayName": "Panelin API Health Check",
    "monitoredResource": {
        "type": "uptime_url",
        "labels": {
            "host": "${SERVICE_URL#https://}"
        }
    },
    "httpCheck": {
        "path": "/health",
        "port": 443,
        "useSsl": true,
        "validateSsl": true,
        "requestMethod": "GET",
        "acceptedResponseStatusCodes": [
            {"statusClass": "STATUS_CLASS_2XX"}
        ]
    },
    "period": "60s",
    "timeout": "10s",
    "contentMatchers": [
        {
            "content": "healthy",
            "matcher": "CONTAINS_STRING"
        }
    ],
    "checkerType": "STATIC_IP_CHECKERS",
    "selectedRegions": [
        "USA",
        "EUROPE",
        "SOUTH_AMERICA"
    ]
}
EOF

    log_info "Uptime check configured for: $SERVICE_URL/health"
    log_info "Apply with: gcloud alpha monitoring uptime create --config-from-file=/tmp/uptime-check.json"
else
    log_warn "Cloud Run service not found, skipping uptime check"
fi

# -----------------------------------------------------------------------------
# Create Custom Dashboard
# -----------------------------------------------------------------------------
log_info "Creating monitoring dashboard..."

cat > /tmp/dashboard.json << 'EOF'
{
  "displayName": "Panelin API Dashboard",
  "gridLayout": {
    "columns": "2",
    "widgets": [
      {
        "title": "Request Count by Response Code",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"panelin-api\" AND metric.type=\"run.googleapis.com/request_count\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_RATE",
                  "groupByFields": ["metric.labels.response_code_class"]
                }
              }
            }
          }]
        }
      },
      {
        "title": "Request Latency (P50, P95, P99)",
        "xyChart": {
          "dataSets": [
            {
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
            },
            {
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"panelin-api\" AND metric.type=\"run.googleapis.com/request_latencies\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_PERCENTILE_99"
                  }
                }
              },
              "legendTemplate": "P99"
            }
          ]
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
        "title": "Cold Start Latency",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"panelin-api\" AND metric.type=\"run.googleapis.com/container/startup_latencies\"",
                "aggregation": {
                  "alignmentPeriod": "300s",
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
EOF

log_info "Dashboard config saved to /tmp/dashboard.json"
log_info "Create with: gcloud monitoring dashboards create --config-from-file=/tmp/dashboard.json"

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo "============================================================================"
echo "Monitoring Setup Complete"
echo "============================================================================"
echo ""
echo "Next steps:"
echo "1. Create alerting policies:"
echo "   Review and apply: monitoring/alerting-policies.yaml"
echo ""
echo "2. Create uptime check:"
echo "   gcloud alpha monitoring uptime create --config-from-file=/tmp/uptime-check.json"
echo ""
echo "3. Create dashboard:"
echo "   gcloud monitoring dashboards create --config-from-file=/tmp/dashboard.json"
echo ""
echo "4. View in Console:"
echo "   https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"
echo ""
echo "============================================================================"
