# Streaky Monitoring with Prometheus & Grafana

## Overview

Streaky API uses **Prometheus** for metrics collection and **Grafana** for visualization and dashboards.

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│ Streaky API │────────▶│  Prometheus  │────────▶│   Grafana   │
│  :8002      │ /metrics│   :9090      │         │   :3000     │
└─────────────┘         └──────────────┘         └─────────────┘
```

## Prometheus Setup

### Installation

**Using Docker (Recommended):**
```bash
docker run -d \
  --name=prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

**Using Homebrew (macOS):**
```bash
brew install prometheus
prometheus --config.file=prometheus.yml
```

### Configuration

The Prometheus configuration is in `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'streaky-api'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['localhost:8002']
```

### Access Prometheus

- **Web UI**: http://localhost:9090
- **Metrics Endpoint**: http://localhost:8002/metrics

## Grafana Setup

### Installation

**Using Docker (Recommended):**
```bash
docker run -d \
  --name=grafana \
  -p 3000:3000 \
  -e "GF_SECURITY_ADMIN_PASSWORD=admin" \
  grafana/grafana
```

**Using Homebrew (macOS):**
```bash
brew install grafana
brew services start grafana
```

### Configuration

1. **Access Grafana**: http://localhost:3000
   - Default credentials: `admin` / `admin`

2. **Add Prometheus Data Source**:
   - Go to Configuration → Data Sources
   - Add Prometheus
   - URL: `http://localhost:9090`
   - Click "Save & Test"

3. **Import Dashboard**:
   - Go to Dashboards → Import
   - Upload `infrastructure/grafana-dashboard.json`
   - Or use dashboard ID: (create and note the ID)

## Available Metrics

### HTTP Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests by method, endpoint, status |
| `http_request_duration_seconds` | Histogram | Request duration in seconds |
| `http_request_size_bytes` | Histogram | Request size in bytes |
| `http_response_size_bytes` | Histogram | Response size in bytes |
| `http_errors_total` | Counter | Total HTTP errors by type |
| `active_requests` | Gauge | Current number of active requests |

### Business Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `habits_created_total` | Counter | Total habits created |
| `entries_logged_total` | Counter | Total entries logged by habit_id |
| `active_habits` | Gauge | Number of active habits |

## Dashboard Panels

The Grafana dashboard includes:

1. **HTTP Request Rate** - Requests per second by endpoint
2. **HTTP Request Duration (p95)** - 95th percentile response time
3. **Error Rate** - Errors per second by type
4. **Active Requests** - Current concurrent requests
5. **Habits Created** - Total habits created counter
6. **Entries Logged** - Total entries logged counter
7. **HTTP Status Codes** - Distribution of status codes
8. **Top Endpoints** - Most requested endpoints

## PromQL Queries

### Request Rate
```promql
rate(http_requests_total[5m])
```

### Error Rate
```promql
rate(http_errors_total[5m])
```

### Average Response Time
```promql
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])
```

### 95th Percentile Response Time
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Top Endpoints
```promql
topk(10, sum by (endpoint) (rate(http_requests_total[5m])))
```

## Alerts

### Recommended Alert Rules

Create `alerts.yml`:

```yaml
groups:
  - name: streaky_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_errors_total[5m]) > 0.1
        for: 5m
        annotations:
          summary: "High error rate detected"
      
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        annotations:
          summary: "Response time p95 > 2s"
      
      - alert: HighActiveRequests
        expr: active_requests > 100
        for: 5m
        annotations:
          summary: "Too many active requests"
```

## Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /healthz` | Simple liveness check |
| `GET /health` | Full health with DB status |
| `GET /version` | App version info |
| `GET /metrics` | Prometheus metrics (text format) |
| `GET /business-metrics` | Business metrics (JSON format) |
| `GET /system` | System resource metrics |

## Production Deployment

### Azure App Service

1. **Deploy Prometheus**:
   - Use Azure Container Instances or VM
   - Or use managed Prometheus service

2. **Deploy Grafana**:
   - Use Azure Container Instances
   - Or use managed Grafana service

3. **Update Prometheus Config**:
   ```yaml
   - targets: ['streaky-api.azurewebsites.net']
     labels:
       environment: 'production'
   ```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8002:8002"
  
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Troubleshooting

### Metrics Not Appearing

1. Check API is running: `curl http://localhost:8002/metrics`
2. Check Prometheus targets: http://localhost:9090/targets
3. Check Prometheus config: `promtool check config prometheus.yml`

### Grafana Not Showing Data

1. Verify Prometheus data source is connected
2. Check time range in Grafana
3. Verify PromQL queries are correct

## Migration from Application Insights

This setup replaces Application Insights. Key differences:

- **Metrics Format**: Prometheus text format vs. Application Insights JSON
- **Scraping**: Pull-based (Prometheus) vs. Push-based (App Insights)
- **Dashboards**: Grafana vs. Azure Portal
- **Cost**: Self-hosted vs. Azure managed service

## Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
