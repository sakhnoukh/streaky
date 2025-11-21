# Azure Setup Guide for Streaky Habit Tracker

This guide walks you through deploying Streaky to Microsoft Azure.

## 📋 Prerequisites

1. **Azure Account** with active subscription
2. **Azure CLI** installed: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
3. **Azure DevOps** account (optional for CI/CD)
4. **Git** installed
5. **Node.js** 18+ and **Python** 3.13+

---

## 🚀 Quick Start: Automated Deployment

The fastest way to deploy is using the provided script:

```bash
# Login to Azure
az login

# Run the automated deployment script
./scripts/deploy-azure.sh
```

Streakypass123!?

This will create all necessary resources. **Save the output** - you'll need the resource names!---

## 📦 Manual Setup (Step-by-Step)

### Step 1: Login to Azure

```bash
az login
```

### Step 2: Create Resource Group

```bash
# Verify your existing resource group
az group show --name BCSAI2025-DEVOPS-STUDENT-1B

# List all resources in the group
az resource list --resource-group BCSAI2025-DEVOPS-STUDENT-1B --output table
```

**Note:** We're using your existing student resource group `BCSAI2025-DEVOPS-STUDENT-1B` instead of creating a new one.

### Step 3: Create Azure SQL Database

```bash
# Create SQL Server
az sql server create \
  --name streaky-sql-server \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --location eastus \
  --admin-user sqladmin \
  --admin-password 'YourSecurePassword123!'

# Allow Azure services to access SQL Server
az sql server firewall-rule create \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --server streaky-sql-server \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Create database
az sql db create \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --server streaky-sql-server \
  --name streaky-db \
  --service-objective Basic \
  --backup-storage-redundancy Local
```

**🔒 Security Note**: For production, use stronger passwords and restrict firewall rules to specific IP ranges.

### Step 4: Create App Service for Backend

```bash
# Create App Service Plan (Linux)
az appservice plan create \
  --name streaky-plan \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --location eastus \
  --is-linux \
  --sku B1

# Create Web App
az webapp create \
  --name streaky-api \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --plan streaky-plan \
  --runtime "PYTHON:3.13"
```

### Step 5: Create Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app streaky-insights \
  --location eastus \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --application-type web

# Get Instrumentation Key
az monitor app-insights component show \
  --app streaky-insights \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --query instrumentationKey \
  --output tsv
```

**📝 Save this key** - you'll need it for environment variables!

### Step 6: Create Storage Account for Frontend

```bash
# Create storage account (name must be globally unique, lowercase, no hyphens)
az storage account create \
  --name streakyfe12345 \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2

# Enable static website hosting
az storage blob service-properties update \
  --account-name streakyfe12345 \
  --static-website \
  --index-document index.html \
  --404-document index.html
```

### Step 7: Configure Web App Environment Variables

```bash
# Set environment variables
az webapp config appsettings set \
  --name streaky-api \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --settings \
    ENVIRONMENT="production" \
    VERSION="1.0.0" \
    AZURE_SQL_SERVER="streaky-sql-server.database.windows.net" \
    AZURE_SQL_DATABASE="streaky-db" \
    AZURE_SQL_USERNAME="sqladmin" \
    AZURE_SQL_PASSWORD="YourSecurePassword123!" \
    APPINSIGHTS_INSTRUMENTATION_KEY="<your-instrumentation-key>" \
    SECRET_KEY="$(openssl rand -hex 32)" \
    ALLOWED_ORIGINS="https://streakyfe12345.z13.web.core.windows.net,http://localhost:5000"
```

### Step 8: Deploy Backend to Azure

```bash
# Option A: Deploy via Azure CLI (from local)
az webapp up \
  --name streaky-api \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --runtime "PYTHON:3.13"

# Option B: Configure Git deployment
az webapp deployment source config-local-git \
  --name streaky-api \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B

# Get Git URL and push
az webapp deployment list-publishing-credentials \
  --name streaky-api \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --query scmUri \
  --output tsv

# Add Azure as remote and push
git remote add azure <git-url-from-above>
git push azure main
```

### Step 9: Run Database Migrations

```bash
# Set environment variables locally to match Azure
export AZURE_SQL_SERVER="streaky-sql-server.database.windows.net"
export AZURE_SQL_DATABASE="streaky-db"
export AZURE_SQL_USERNAME="sqladmin"
export AZURE_SQL_PASSWORD="YourSecurePassword123!"

# Run migrations
python -m alembic upgrade head

# Or use the script
./scripts/run-migrations.sh
```

### Step 10: Deploy Frontend to Azure Storage

```bash
# Build frontend with Azure API URL
cd frontend
echo "VITE_API_URL=https://streaky-api.azurewebsites.net" > .env
npm install
npm run build

# Upload to Azure Storage
az storage blob upload-batch \
  --account-name streakyfe12345 \
  --source ./dist \
  --destination '$web' \
  --overwrite

# Or use the script
cd ..
./scripts/deploy-frontend.sh streakyfe12345
```

---

## 🔧 Azure DevOps Setup (CI/CD)

### Step 1: Create Azure DevOps Organization

1. Go to https://dev.azure.com
2. Click "New Organization"
3. Name it (e.g., "streaky-devops")

### Step 2: Create Project

1. Click "New Project"
2. Name: "Streaky"
3. Visibility: Private
4. Create

### Step 3: Connect GitHub Repository

1. In Azure DevOps, go to **Repos** > **Files**
2. Click "Import a repository"
3. Select "Import from GitHub"
4. Authorize Azure DevOps to access GitHub
5. Select `sakhnoukh/streaky` repository
6. Import

### Step 4: Create Service Connection

1. Go to **Project Settings** (bottom left)
2. Click **Service connections**
3. Click **New service connection**
4. Select **Azure Resource Manager**
5. Choose **Service principal (automatic)**
6. Select your subscription
7. Resource group: `streaky-prod-rg`
8. Name: `streaky-azure-connection`
9. Grant access to all pipelines
10. **Save**

### Step 5: Create Pipeline

1. Go to **Pipelines** > **Pipelines**
2. Click "New Pipeline"
3. Select "Azure Repos Git" (or "GitHub" if you didn't import)
4. Select `streaky` repository
5. Select "Existing Azure Pipelines YAML file"
6. Path: `/azure-pipelines.yml`
7. Review the pipeline
8. **Update variables in pipeline** (already set correctly):
   ```yaml
   variables:
     azureServiceConnection: 'streaky-azure-connection'
     webAppName: 'streaky-api'
     resourceGroup: 'BCSAI2025-DEVOPS-STUDENT-1B'
   ```
9. Click "Run"

### Step 6: Create Environments

1. Go to **Pipelines** > **Environments**
2. Create two environments:
   - Name: `staging`, Description: "Staging environment"
   - Name: `production`, Description: "Production environment"
3. Add approval checks for production (optional but recommended):
   - Click `production` environment
   - Click "..." > "Approvals and checks"
   - Add "Approvals"
   - Select approvers
   - Save

### Step 7: Configure Azure Boards

1. Go to **Boards** > **Backlogs**
2. Click "New Work Item" > "Epic"
3. Create epics for:
   - Azure Migration
   - Monitoring Setup
   - Documentation
4. Break down into Features and User Stories
5. Create Sprint (Iteration):
   - Go to **Project Settings** > **Project configuration**
   - Click "Iterations"
   - Add sprint dates (Nov 21 - Dec 4)

---

## 📊 Application Insights Dashboards

### Step 1: Access Application Insights

1. Go to Azure Portal: https://portal.azure.com
2. Navigate to **Resource Groups** > `BCSAI2025-DEVOPS-STUDENT-1B`
3. Click on `streaky-insights`

### Step 2: Create Custom Dashboard

1. Click "Overview"
2. Click "Dashboard" at top
3. Click "+ New dashboard"
4. Name: "Streaky Monitoring"

### Step 3: Add Widgets

Add these widgets to monitor your app:

**Performance Monitoring:**
- Server response time (P50, P95, P99)
- Failed requests
- Server requests (requests/min)
- Availability

**Business Metrics:**
- Custom events (habit created, entry logged)
- Custom metrics (active users, streak milestones)

**Error Tracking:**
- Exceptions
- Failed dependency calls
- 4xx/5xx errors

### Step 4: Set Up Alerts

1. Click "Alerts" in Application Insights
2. Create alert rules:
   - **High Error Rate**: Failed requests > 5% in 5 min
   - **Slow Response**: Server response time > 2000ms
   - **Service Down**: Availability < 99%
3. Configure action groups (email notifications)

---

## 🔍 Verification Steps

After deployment, verify everything works:

### 1. Backend Health Check

```bash
curl https://streaky-api.azurewebsites.net/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0",
  "database": {
    "status": "healthy",
    "type": "Azure SQL"
  }
}
```

### 2. Frontend Access

Open in browser:
```
https://streakyfe12345.z13.web.core.windows.net
```

### 3. Test Full Flow

1. Login with `testuser` / `testpass`
2. Create a habit
3. Log an entry
4. Check Application Insights for telemetry

### 4. Check Logs

```bash
# Stream App Service logs
az webapp log tail --name streaky-api --resource-group BCSAI2025-DEVOPS-STUDENT-1B

# View Application Insights logs
# Go to Azure Portal > Application Insights > Logs
# Run query:
traces
| where timestamp > ago(1h)
| order by timestamp desc
```

---

## 🎯 Common Issues & Troubleshooting

### Issue: Database Connection Fails

**Solution:**
- Check firewall rules: `az sql server firewall-rule list`
- Verify connection string in App Service settings
- Check SQL admin password

### Issue: Application Insights Not Showing Data

**Solution:**
- Verify instrumentation key is set correctly
- Check App Service logs for errors
- Wait 5-10 minutes for data to appear

### Issue: Frontend Can't Connect to Backend

**Solution:**
- Verify CORS settings in backend
- Check API URL in frontend `.env`
- Verify both apps are deployed

### Issue: Pipeline Fails to Deploy

**Solution:**
- Check service connection permissions
- Verify App Service name matches pipeline variable
- Check deployment logs in Azure DevOps

---

## 📝 Cost Estimation

| Resource | Tier | Monthly Cost (Est.) |
|----------|------|---------------------|
| App Service Plan (B1) | Basic | ~$13 |
| Azure SQL (Basic) | Basic | ~$5 |
| Storage Account | Standard | ~$1 |
| Application Insights | Pay-as-you-go | ~$2-5 |
| **Total** | | **~$21-24/month** |

💡 **Tip**: Use Azure Calculator for precise estimates: https://azure.microsoft.com/pricing/calculator/

---

## 🎓 Next Steps

After successful deployment:

1. ✅ **Test thoroughly** - Create test habits, log entries
2. ✅ **Set up monitoring** - Configure alerts in Application Insights
3. ✅ **Document deployment** - Take screenshots for your Sprint Review
4. ✅ **Create Scrum artifacts** - Update Azure Boards with completed work
5. ✅ **Prepare demo** - Practice showing the live Azure deployment

---

## 📚 Additional Resources

- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Azure SQL Documentation](https://docs.microsoft.com/azure/azure-sql/)
- [Application Insights Documentation](https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [Azure DevOps Pipelines](https://docs.microsoft.com/azure/devops/pipelines/)
- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)

---

## 🆘 Support

If you encounter issues:
1. Check logs in Azure Portal
2. Review Application Insights for errors
3. Check Azure DevOps pipeline logs
4. Review this documentation
5. Ask your team members

Good luck with your deployment! 🚀
