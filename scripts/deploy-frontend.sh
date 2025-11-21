#!/bin/bash
# Deploy React Frontend to Azure Storage Static Website

set -e

STORAGE_ACCOUNT="$1"

if [ -z "$STORAGE_ACCOUNT" ]; then
    echo "Usage: ./deploy-frontend.sh <storage-account-name>"
    exit 1
fi

echo "🎨 Building React Frontend..."
cd frontend
npm install
npm run build

echo "☁️  Deploying to Azure Storage: $STORAGE_ACCOUNT..."
az storage blob upload-batch \
  --account-name $STORAGE_ACCOUNT \
  --source ./dist \
  --destination '$web' \
  --overwrite

FRONTEND_URL="https://${STORAGE_ACCOUNT}.z13.web.core.windows.net"

echo "✅ Frontend deployed successfully!"
echo "🌐 URL: $FRONTEND_URL"
