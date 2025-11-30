# Streaky Monitoring & Dashboards

## Azure Resources

| Resource | Type | Location |
|----------|------|----------|
| `streaky-api` | App Service | Canada Central |
| `streaky-sql-server/streaky-db` | SQL Database | East US |
| `Streaky-insights` | Application Insights | West Europe |

## Application Insights Dashboard

Access the dashboard at: [Azure Portal - Streaky Insights](https://portal.azure.com/#@/resource/subscriptions/e0b9cada-61bc-4b5a-bd7a-52c606726b3b/resourceGroups/BCSAI2025-DEVOPS-STUDENT-1B/providers/microsoft.insights/components/Streaky-insights/overview)

### Key Metrics

#### 1. Availability / Uptime (%)
```kusto
requests
| summarize availability = round(100.0 * countif(success == true) / count(), 2) by bin(timestamp, 1h)
| render timechart
```

#### 2. Average Response Time (ms)
```kusto
requests
| summarize avgDuration = avg(duration) by bin(timestamp, 5m)
| render timechart
```

#### 3. Error Rate (%)
```kusto
requests
| summarize errorRate = round(100.0 * countif(success == false) / count(), 2) by bin(timestamp, 1h)
| render timechart
```

#### 4. Request Count
```kusto
requests
| summarize requestCount = count() by bin(timestamp, 5m)
| render barchart
```

#### 5. Failed Requests by Endpoint
```kusto
requests
| where success == false
| summarize failedCount = count() by name
| order by failedCount desc
| render piechart
```

#### 6. Response Time by Endpoint
```kusto
requests
| summarize avgDuration = avg(duration), p95Duration = percentile(duration, 95) by name
| order by avgDuration desc
```

## Creating a Dashboard

### Option 1: Azure Portal (Recommended)

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Streaky-insights** Application Insights
3. Click **Workbooks** > **New**
4. Add the KQL queries above as separate tiles
5. Save the workbook as "Streaky Monitoring Dashboard"

### Option 2: Pin to Dashboard

1. Go to **Streaky-insights** > **Logs**
2. Run each query above
3. Click **Pin to dashboard** for each result
4. Select or create "Streaky Monitoring Dashboard"

## Alerts Configuration

### Recommended Alerts

| Alert | Condition | Threshold |
|-------|-----------|-----------|
| High Error Rate | Error rate > 5% | 5 minutes |
| Slow Response | Avg response > 2000ms | 5 minutes |
| Service Down | Availability < 99% | 5 minutes |

### Creating an Alert

```bash
# Example: Create high error rate alert
az monitor metrics alert create \
  --name "High Error Rate - Streaky" \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --scopes /subscriptions/e0b9cada-61bc-4b5a-bd7a-52c606726b3b/resourceGroups/BCSAI2025-DEVOPS-STUDENT-1B/providers/microsoft.insights/components/Streaky-insights \
  --condition "avg requests/failed > 5" \
  --window-size 5m \
  --evaluation-frequency 1m
```

## Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /healthz` | Simple liveness check |
| `GET /health` | Full health with DB status |
| `GET /version` | App version info |
| `GET /metrics` | Business metrics |
| `GET /system` | System resource metrics |

## Live URLs

- **API**: https://streaky-api.azurewebsites.net
- **Health Check**: https://streaky-api.azurewebsites.net/health
- **API Docs**: https://streaky-api.azurewebsites.net/docs
- **Application Insights**: [Azure Portal](https://portal.azure.com/#blade/AppInsightsExtension/QuickPulseBladeV2/ComponentId/%7B%22Name%22%3A%22Streaky-insights%22%2C%22SubscriptionId%22%3A%22e0b9cada-61bc-4b5a-bd7a-52c606726b3b%22%2C%22ResourceGroup%22%3A%22BCSAI2025-DEVOPS-STUDENT-1B%22%7D)
