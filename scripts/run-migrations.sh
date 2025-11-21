#!/bin/bash
# Run Alembic migrations on Azure SQL Database

set -e

echo "🔄 Running database migrations on Azure..."

# Check if Azure SQL environment variables are set
if [ -z "$AZURE_SQL_SERVER" ] || [ -z "$AZURE_SQL_USERNAME" ] || [ -z "$AZURE_SQL_PASSWORD" ]; then
    echo "❌ Error: Azure SQL environment variables not set"
    echo "Please set: AZURE_SQL_SERVER, AZURE_SQL_USERNAME, AZURE_SQL_PASSWORD"
    exit 1
fi

# Run migrations
echo "📊 Executing alembic upgrade head..."
python -m alembic upgrade head

echo "✅ Migrations completed successfully!"
echo ""
echo "🔍 Verify migrations:"
echo "python -m alembic current"
