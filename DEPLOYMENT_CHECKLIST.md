# 🚀 Streaky Azure Deployment Checklist

## ✅ Code Implementation Status

All Azure-ready code has been implemented! Here's what was added:

### Backend Changes (8 files modified/added)
- ✅ `requirements.txt` - Added Azure dependencies
- ✅ `app/config.py` - Azure SQL + App Insights configuration
- ✅ `app/db.py` - Azure SQL support with connection pooling
- ✅ `app/main.py` - Monitoring middleware + CORS for Azure
- ✅ `app/monitoring.py` - Application Insights integration (NEW)
- ✅ `app/routers/monitoring.py` - Health checks & metrics (NEW)
- ✅ `.env.example` - Complete Azure configuration template

### Frontend Changes (2 files modified/added)
- ✅ `frontend/src/App.jsx` - Environment-based API URLs
- ✅ `frontend/.env.example` - API URL configuration

### CI/CD & Deployment (4 files added)
- ✅ `azure-pipelines.yml` - Complete CI/CD pipeline (NEW)
- ✅ `scripts/deploy-azure.sh` - Automated Azure setup (NEW)
- ✅ `scripts/deploy-frontend.sh` - Frontend deployment (NEW)
- ✅ `scripts/run-migrations.sh` - Database migrations (NEW)

### Documentation (1 file added)
- ✅ `AZURE_SETUP.md` - Comprehensive setup guide (NEW)

---

## 📋 YOUR ACTION ITEMS

### Phase 1: Azure Portal Setup (30-45 minutes)

#### Option A: Automated (Recommended)
```bash
# 1. Login to Azure
az login

# 2. Run automated deployment
./scripts/deploy-azure.sh

# 3. Save all the resource names from the output!
```

#### Option B: Manual Setup
Follow `AZURE_SETUP.md` Step-by-Step section

**Resources to Create:**
- [ ] Resource Group: `streaky-prod-rg`
- [ ] SQL Server: `streaky-sql-server`
- [ ] SQL Database: `streaky-db`
- [ ] App Service Plan: `streaky-plan`
- [ ] Web App: `streaky-api`
- [ ] Application Insights: `streaky-insights`
- [ ] Storage Account: `streakyfe<unique>`

**Save These Values:**
- SQL Server admin password
- Application Insights instrumentation key
- Storage account name
- Web App URL

---

### Phase 2: Environment Configuration (15 minutes)

#### 1. Update Local `.env` for Azure
```bash
# Copy example
cp .env.example .env

# Edit .env and add your Azure values:
nano .env  # or use your editor
```

Add:
```env
ENVIRONMENT=production
AZURE_SQL_SERVER=streaky-sql-server.database.windows.net
AZURE_SQL_DATABASE=streaky-db
AZURE_SQL_USERNAME=sqladmin
AZURE_SQL_PASSWORD=<your-password>
APPINSIGHTS_INSTRUMENTATION_KEY=<your-key>
SECRET_KEY=<generate-with-openssl-rand-hex-32>
```

#### 2. Update Azure App Service Settings
```bash
az webapp config appsettings set \
  --name streaky-api \
  --resource-group streaky-prod-rg \
  --settings \
    ENVIRONMENT="production" \
    AZURE_SQL_SERVER="streaky-sql-server.database.windows.net" \
    AZURE_SQL_DATABASE="streaky-db" \
    AZURE_SQL_USERNAME="sqladmin" \
    AZURE_SQL_PASSWORD="<your-password>" \
    APPINSIGHTS_INSTRUMENTATION_KEY="<your-key>" \
    SECRET_KEY="$(openssl rand -hex 32)"
```

---

### Phase 3: Database Migration (10 minutes)

```bash
# Set environment variables locally
export AZURE_SQL_SERVER="streaky-sql-server.database.windows.net"
export AZURE_SQL_DATABASE="streaky-db"
export AZURE_SQL_USERNAME="sqladmin"
export AZURE_SQL_PASSWORD="<your-password>"

# Run migrations
python -m alembic upgrade head
```

---

### Phase 4: Deploy Backend (15 minutes)

```bash
# Option A: Azure CLI
az webapp up \
  --name streaky-api \
  --resource-group streaky-prod-rg \
  --runtime "PYTHON:3.13"

# Option B: Git Push
az webapp deployment source config-local-git \
  --name streaky-api \
  --resource-group streaky-prod-rg

# Get git URL and push
git remote add azure <url>
git push azure feat/product-improvements:main
```

---

### Phase 5: Deploy Frontend (10 minutes)

```bash
# Update frontend API URL
cd frontend
echo "VITE_API_URL=https://streaky-api.azurewebsites.net" > .env

# Build and deploy
npm install
npm run build

# Upload to Azure Storage
az storage blob upload-batch \
  --account-name <your-storage-account> \
  --source ./dist \
  --destination '$web' \
  --overwrite
```

---

### Phase 6: Azure DevOps Setup (45 minutes)

#### 1. Create Organization & Project
- Go to https://dev.azure.com
- Create organization (e.g., "streaky-devops")
- Create project: "Streaky"

#### 2. Import Repository
- Go to Repos > Import
- Import from GitHub: `sakhnoukh/streaky`

#### 3. Create Service Connection
- Project Settings > Service connections
- New > Azure Resource Manager
- Name: `streaky-azure-connection`
- Subscription: Your subscription
- Resource Group: `streaky-prod-rg`

#### 4. Create Pipeline
- Pipelines > New Pipeline
- Select Azure Repos
- Existing YAML: `/azure-pipelines.yml`
- Update variables:
  ```yaml
  azureServiceConnection: 'streaky-azure-connection'
  webAppName: 'streaky-api'
  resourceGroup: 'streaky-prod-rg'
  ```
- Run pipeline

#### 5. Create Environments
- Pipelines > Environments
- Create: `staging`
- Create: `production` (add approvals)

#### 6. Setup Azure Boards
- Boards > Backlogs
- Create Epics:
  - Azure Migration
  - Monitoring Setup
  - Documentation
- Break down into User Stories
- Create Sprint (Nov 21 - Dec 4)

---

### Phase 7: Application Insights Setup (30 minutes)

#### 1. Access Application Insights
- Azure Portal > `streaky-insights`

#### 2. Create Dashboard
- Dashboard > New > "Streaky Monitoring"
- Add widgets:
  - Server response time
  - Failed requests
  - Availability
  - Custom events

#### 3. Set Up Alerts
- Alerts > New Alert Rule
- Create alerts for:
  - Error rate > 5%
  - Response time > 2s
  - Availability < 99%

---

### Phase 8: Verification (15 minutes)

#### 1. Test Backend
```bash
curl https://streaky-api.azurewebsites.net/health
```

Expected:
```json
{
  "status": "healthy",
  "environment": "production",
  "database": {"status": "healthy", "type": "Azure SQL"}
}
```

#### 2. Test Frontend
Open: `https://<storage-account>.z13.web.core.windows.net`

#### 3. Test Full Flow
1. Login
2. Create habit
3. Log entry
4. Check Application Insights

#### 4. Check Logs
```bash
az webapp log tail --name streaky-api --resource-group streaky-prod-rg
```

---

## 📊 Monitoring Checklist

After deployment, ensure you have:

- [ ] Application Insights showing telemetry
- [ ] Custom dashboard created
- [ ] Alerts configured
- [ ] Logs streaming successfully
- [ ] All health checks passing

---

## 📝 Documentation Checklist

Create these Scrum artifacts:

- [ ] Product Backlog in Azure Boards
- [ ] Sprint 1 documentation (Goals, Stories, Retrospective)
- [ ] Sprint 2 documentation
- [ ] Architecture diagram (draw.io recommended)
- [ ] Team roles and rotation schedule
- [ ] Definition of Done updated
- [ ] Individual contribution statements

---

## 🎯 Final Checklist Before Demo

- [ ] Backend deployed and healthy
- [ ] Frontend deployed and accessible
- [ ] Database migrations applied
- [ ] CI/CD pipeline running successfully
- [ ] Application Insights showing data
- [ ] Dashboards created
- [ ] All endpoints tested
- [ ] Scrum artifacts complete
- [ ] Architecture diagram ready
- [ ] Demo script prepared

---

## 💡 Quick Tips

**Common Commands:**
```bash
# Check deployment status
az webapp show --name streaky-api --resource-group streaky-prod-rg

# View app logs
az webapp log tail --name streaky-api --resource-group streaky-prod-rg

# Restart app
az webapp restart --name streaky-api --resource-group streaky-prod-rg

# Check pipeline status
az pipelines run list --project Streaky --output table
```

**Troubleshooting:**
- Backend not working? Check Application Insights logs
- Frontend can't connect? Verify CORS settings
- Database errors? Check firewall rules
- Pipeline failing? Check service connection

---

## 📚 Documentation Files

- **AZURE_SETUP.md** - Complete Azure setup guide
- **DEPLOYMENT_CHECKLIST.md** - This file
- **README.md** - General project documentation
- **CONTRIBUTING.md** - Development workflow

---

## 🆘 Need Help?

1. Check logs in Azure Portal
2. Review Application Insights
3. Check Azure DevOps pipeline logs
4. Review AZURE_SETUP.md
5. Ask team members

---

## 🎉 Success Criteria

Your deployment is successful when:
- ✅ All Azure resources created
- ✅ Backend deployed and responding
- ✅ Frontend deployed and accessible
- ✅ Database connected and migrated
- ✅ CI/CD pipeline running
- ✅ Application Insights showing data
- ✅ All health checks passing
- ✅ Full user flow working (login → create → log → view)

Good luck! 🚀
