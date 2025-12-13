#!/bin/bash

# Quick Reference: Railway Backend Update
# ========================================

echo "🚀 Railway Backend Update - Quick Reference"
echo "==========================================="
echo ""
echo "New Backend URL: https://meal-planner.up.railway.app"
echo "Frontend Dev URL: http://localhost:3000"
echo ""

echo "📋 Status Check"
echo "---------------"
echo ""

# Check backend health
echo "1. Backend Health:"
HEALTH=$(curl -s https://meal-planner.up.railway.app/health | jq -r '.status' 2>/dev/null || echo "error")
if [ "$HEALTH" = "healthy" ] || [ "$HEALTH" = "degraded" ]; then
    echo "   ✅ Backend is accessible (status: $HEALTH)"
else
    echo "   ❌ Backend not accessible"
fi

# Check frontend server
echo ""
echo "2. Frontend Server:"
if pgrep -f "next dev" > /dev/null; then
    echo "   ✅ Frontend is running"
    echo "   🌐 http://localhost:3000"
else
    echo "   ⚠️  Frontend not running"
    echo "   Start with: cd frontend && npm run dev"
fi

# Check configuration
echo ""
echo "3. Configuration:"
if [ -f "/home/darae/meal-planner/frontend/.env.local" ]; then
    echo "   ✅ .env.local exists"
    cat /home/darae/meal-planner/frontend/.env.local | grep -v "^#"
else
    echo "   ❌ .env.local missing"
fi

echo ""
echo "📝 Next Steps"
echo "-------------"
echo ""
echo "⚠️  IMPORTANT: Database migration required"
echo ""
echo "Option 1 - Redeploy (Automatic):"
echo "  git add backend/Dockerfile backend/Procfile"
echo "  git commit -m 'Add automatic migrations'"
echo "  git push"
echo "  # Railway will auto-deploy and run migrations"
echo ""
echo "Option 2 - Manual Migration:"
echo "  railway run alembic upgrade head"
echo ""
echo "After migration, test with:"
echo "  node frontend/test-e2e-integration.js"
echo ""
echo "📚 Documentation:"
echo "  - RAILWAY_UPDATE_COMPLETE.md (Quick summary)"
echo "  - RAILWAY_UPDATE_SUMMARY.md (Detailed info)"
echo "  - RAILWAY_INTEGRATION_TEST_REPORT.md (Test details)"
echo ""
