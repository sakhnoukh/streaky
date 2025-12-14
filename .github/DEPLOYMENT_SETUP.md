# 🚀 GitHub Actions Azure Deployment Setup

This guide will help you configure GitHub Actions to automatically deploy to Azure on every push.

## 📋 Prerequisites

1. Azure resources already created (App Service, Storage Account, etc.)
2. GitHub repository with Actions enabled
3. Azure CLI installed locally (for getting publish profile)

## 🔑 Required GitHub Secrets

You need to add these secrets to your GitHub repository:

### 1. Get Azure Web App Publish Profile

```bash
# Login to Azure
az login

# Download publish profile
az webapp deployment list-publishing-profiles \
  --name streaky-api \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --xml > publish-profile.xml
```

Then copy the entire XML content and add it as a GitHub secret:

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
4. Value: Paste the entire XML content from `publish-profile.xml`

### 2. Get Azure Storage Account Key

```bash
# Get storage account key
az storage account keys list \
  --account-name streakyfelix \
  --resource-group BCSAI2025-DEVOPS-STUDENT-1B \
  --query "[0].value" \
  --output tsv
```

Add as GitHub secret:
- Name: `AZURE_STORAGE_KEY`
- Value: The key from the command above

### 3. (Optional) Azure Credentials for CLI

If you want to use Azure CLI in workflows:

```bash
# Create service principal
az ad sp create-for-rbac \
  --name "github-actions-streaky" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/BCSAI2025-DEVOPS-STUDENT-1B \
  --sdk-auth
```

Copy the JSON output and add as GitHub secret:
- Name: `AZURE_CREDENTIALS`
- Value: The entire JSON output

## 🎯 Deployment Behavior

### Automatic Deployment

- **Main branch**: Deploys to **production** (streaky-api.azurewebsites.net)
- **Develop branch**: Deploys to **staging** slot (if configured)

### Manual Deployment

You can also trigger deployments manually:

1. Go to **Actions** tab in GitHub
2. Select **Deploy to Azure** workflow
3. Click **Run workflow**
4. Choose branch and click **Run workflow**

## 📝 Workflow Files

- `.github/workflows/ci.yml` - Main CI/CD pipeline (tests + deployment)
- `.github/workflows/deploy.yml` - Dedicated deployment workflow

## 🔍 Verification

After pushing to main/develop:

1. Check GitHub Actions tab for workflow run
2. Verify deployment succeeded
3. Test the deployed API:
   - Production: https://streaky-api.azurewebsites.net/health
   - Frontend: https://streakyfelix.z6.web.core.windows.net

## 🐛 Troubleshooting

### Deployment fails with "Publish profile not found"
- Make sure `AZURE_WEBAPP_PUBLISH_PROFILE` secret is set correctly
- Verify the XML content is complete (should start with `<publishData>`)

### Frontend deployment fails
- Check `AZURE_STORAGE_KEY` secret is correct
- Verify storage account name matches (currently: `streakyfelix`)

### Database migrations not running
- Migrations need to be configured in Azure App Service
- Or add a deployment script step in the workflow

## 📚 Additional Resources

- [Azure App Service Deployment](https://docs.microsoft.com/en-us/azure/app-service/deploy-github-actions)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
