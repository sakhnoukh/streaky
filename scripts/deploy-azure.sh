#!/bin/bash
# Azure Deployment Script for Streaky Habit Tracker
# This script creates all necessary Azure resources

set -e  # Exit on error

# Configuration
RESOURCE_GROUP="streaky-prod-rg"
LOCATION="eastus"
SQL_SERVER="streaky-sql-server"
SQL_DATABASE="streaky-db"
SQL_ADMIN="sqladmin"
APP_SERVICE_PLAN="streaky-plan"
WEB_APP="streaky-api"
STORAGE_ACCOUNT="streakyfe$(date +%s)"  # Add timestamp for uniqueness
APP_INSIGHTS="streaky-insights"

echo "🚀 Starting Azure Deployment for Streaky..."

# 1. Create Resource Group
echo "📦 Creating Resource Group: $RESOURCE_GROUP"
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# 2. Create Azure SQL Server
echo "💾 Creating Azure SQL Server: $SQL_SERVER"
read -sp "Enter SQL Admin Password: " SQL_PASSWORD
echo

az sql server create \
  --name $SQL_SERVER \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --admin-user $SQL_ADMIN \
  --admin-password "$SQL_PASSWORD"

# 3. Configure SQL Server Firewall (Allow Azure Services)
echo "🔒 Configuring SQL Server Firewall..."
az sql server firewall-rule create \
  --resource-group $RESOURCE_GROUP \
  --server $SQL_SERVER \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# 4. Create SQL Database
echo "🗄️  Creating SQL Database: $SQL_DATABASE"
az sql db create \
  --resource-group $RESOURCE_GROUP \
  --server $SQL_SERVER \
  --name $SQL_DATABASE \
  --service-objective Basic \
  --backup-storage-redundancy Local

# 5. Create App Service Plan
echo "📱 Creating App Service Plan: $APP_SERVICE_PLAN"
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --is-linux \
  --sku B1

# 6. Create Web App
echo "🌐 Creating Web App: $WEB_APP"
az webapp create \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --runtime "PYTHON:3.13"

# 7. Create Application Insights
echo "📊 Creating Application Insights: $APP_INSIGHTS"
az monitor app-insights component create \
  --app $APP_INSIGHTS \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --application-type web

# Get Application Insights Instrumentation Key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app $APP_INSIGHTS \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey \
  --output tsv)

# 8. Create Storage Account for Frontend
echo "💿 Creating Storage Account: $STORAGE_ACCOUNT"
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2

# Enable static website hosting
az storage blob service-properties update \
  --account-name $STORAGE_ACCOUNT \
  --static-website \
  --index-document index.html \
  --404-document index.html

# 9. Configure Web App Settings
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
    ALLOWED_ORIGINS="https://${STORAGE_ACCOUNT}.z13.web.core.windows.net,http://localhost:5000"

# 10. Create Deployment Slot for Staging
echo "🎭 Creating Staging Deployment Slot..."
az webapp deployment slot create \
  --name $WEB_APP \
  --resource-group $RESOURCE_GROUP \
  --slot staging

echo "✅ Azure Deployment Complete!"
echo ""
echo "📋 Resource Summary:"
echo "-------------------"
echo "Resource Group: $RESOURCE_GROUP"
echo "SQL Server: ${SQL_SERVER}.database.windows.net"
echo "SQL Database: $SQL_DATABASE"
echo "Web App: https://${WEB_APP}.azurewebsites.net"
echo "Storage Account: $STORAGE_ACCOUNT"
echo "Frontend URL: https://${STORAGE_ACCOUNT}.z13.web.core.windows.net"
echo "App Insights: $APP_INSIGHTS"
echo ""
echo "🔑 Next Steps:"
echo "1. Run database migrations: ./scripts/run-migrations.sh"
echo "2. Deploy backend: git push azure main"
echo "3. Deploy frontend: ./scripts/deploy-frontend.sh"
echo "4. Configure Azure DevOps Pipeline"
