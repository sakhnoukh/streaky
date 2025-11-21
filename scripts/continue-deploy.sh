#!/bin/bash
# Continue Azure Deployment (after SQL Server/DB created)
# Uses FREE tier to avoid quota issues on student subscriptions

set -e  # Exit on error

# Configuration (must match deploy-azure.sh)
RESOURCE_GROUP="BCSAI2025-DEVOPS-STUDENT-1B"
LOCATION="eastus"
SQL_SERVER="streaky-sql-server"
SQL_DATABASE="streaky-db"
SQL_ADMIN="sqladmin"
APP_SERVICE_PLAN="streaky-plan"
WEB_APP="streaky-api"
STORAGE_ACCOUNT="streakyfe$(date +%s)"  # Add timestamp for uniqueness
APP_INSIGHTS="streaky-insights"

echo "🔄 Continuing Azure Deployment for Streaky..."
echo ""

# Get SQL password (you'll need to enter it again)
read -sp "Enter SQL Admin Password (same as before): " SQL_PASSWORD
echo ""
echo ""

# 1. Create App Service Plan (FREE tier for student subscription)
echo "📱 Creating App Service Plan (FREE tier): $APP_SERVICE_PLAN"
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --is-linux \
  --sku F1

echo "✅ App Service Plan created"

# 2. Create Web App
echo "🌐 Creating Web App: $WEB_APP"
az webapp create \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --runtime "PYTHON:3.11"

echo "✅ Web App created"

# 3. Create Application Insights
echo "📊 Creating Application Insights: $APP_INSIGHTS"
az monitor app-insights component create \
  --app $APP_INSIGHTS \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --application-type web

echo "✅ Application Insights created"

# Get Application Insights Instrumentation Key
echo "🔑 Retrieving Application Insights Key..."
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app $APP_INSIGHTS \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey \
  --output tsv)

echo "✅ Instrumentation Key retrieved"

# 4. Create Storage Account for Frontend
echo "💿 Creating Storage Account: $STORAGE_ACCOUNT"
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2

echo "✅ Storage Account created"

# Enable static website hosting
echo "🌐 Enabling static website hosting..."
az storage blob service-properties update \
  --account-name $STORAGE_ACCOUNT \
  --static-website \
  --index-document index.html \
  --404-document index.html

echo "✅ Static website hosting enabled"

# 5. Configure Web App Settings
echo "⚙️  Configuring Web App Environment Variables..."
az webapp config appsettings set \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --settings \
    ENVIRONMENT="production" \
    VERSION="1.0.0" \
    AZURE_SQL_SERVER="${SQL_SERVER}.database.windows.net" \
    AZURE_SQL_DATABASE="$SQL_DATABASE" \
    AZURE_SQL_USERNAME="$SQL_ADMIN" \
    AZURE_SQL_PASSWORD="$SQL_PASSWORD" \
    APPINSIGHTS_INSTRUMENTATION_KEY="$INSTRUMENTATION_KEY" \
    SECRET_KEY="$(openssl rand -hex 32)" \
    ALLOWED_ORIGINS="https://${STORAGE_ACCOUNT}.z13.web.core.windows.net,http://localhost:5000" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    WEBSITES_PORT="8000"

echo "✅ Environment variables configured"

# 6. Configure startup command
echo "🚀 Configuring startup command..."
az webapp config set \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --startup-file "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo "✅ Startup command configured"

echo ""
echo "✅ ✅ ✅ Azure Deployment Complete! ✅ ✅ ✅"
echo ""
echo "📋 Resource Summary:"
echo "===================="
echo "Resource Group: $RESOURCE_GROUP"
echo ""
echo "🗄️  Database:"
echo "   SQL Server: ${SQL_SERVER}.database.windows.net"
echo "   Database: $SQL_DATABASE"
echo "   Username: $SQL_ADMIN"
echo ""
echo "🌐 Backend:"
echo "   Web App: https://${WEB_APP}.azurewebsites.net"
echo "   API Docs: https://${WEB_APP}.azurewebsites.net/docs"
echo "   Health Check: https://${WEB_APP}.azurewebsites.net/health"
echo ""
echo "🎨 Frontend:"
echo "   Storage Account: $STORAGE_ACCOUNT"
echo "   Frontend URL: https://${STORAGE_ACCOUNT}.z13.web.core.windows.net"
echo ""
echo "📊 Monitoring:"
echo "   Application Insights: $APP_INSIGHTS"
echo "   Instrumentation Key: $INSTRUMENTATION_KEY"
echo ""
echo "🔑 IMPORTANT - Save these values!"
echo "================================"
echo "SQL Admin Password: [the password you entered]"
echo "App Insights Key: $INSTRUMENTATION_KEY"
echo "Storage Account: $STORAGE_ACCOUNT"
echo ""
echo "🎯 Next Steps:"
echo "=============="
echo "1. Run database migrations:"
echo "   export AZURE_SQL_SERVER=\"${SQL_SERVER}.database.windows.net\""
echo "   export AZURE_SQL_DATABASE=\"$SQL_DATABASE\""
echo "   export AZURE_SQL_USERNAME=\"$SQL_ADMIN\""
echo "   export AZURE_SQL_PASSWORD=\"[your-password]\""
echo "   python -m alembic upgrade head"
echo ""
echo "2. Deploy backend code:"
echo "   az webapp up --name $WEB_APP --resource-group $RESOURCE_GROUP"
echo ""
echo "3. Deploy frontend:"
echo "   cd frontend"
echo "   echo \"VITE_API_URL=https://${WEB_APP}.azurewebsites.net\" > .env"
echo "   npm install && npm run build"
echo "   az storage blob upload-batch --account-name $STORAGE_ACCOUNT --source ./dist --destination '\$web' --overwrite"
echo ""
echo "4. Test your deployment:"
echo "   curl https://${WEB_APP}.azurewebsites.net/health"
echo ""
