#!/bin/bash
# Run database migrations on Railway

echo "=========================================="
echo "Running Database Migrations"
echo "=========================================="
echo ""

# Check if Railway CLI is set up
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not installed"
    exit 1
fi

# Check if project is linked
if ! railway status &> /dev/null; then
    echo "❌ Railway project not linked"
    echo "Run: railway link"
    exit 1
fi

echo "Running Alembic migrations via Railway..."
echo ""

# Run migrations using Railway CLI
railway run alembic upgrade head

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrations completed successfully!"
    echo ""
    echo "Database tables created:"
    echo "  - users"
    echo "  - recipes"
    echo "  - ingredients"
    echo "  - meal_plans"
    echo "  - and more..."
else
    echo ""
    echo "❌ Migration failed"
    echo ""
    echo "Try manually:"
    echo "  railway run python -c \"from app.database import Base, engine; Base.metadata.create_all(engine)\""
fi
