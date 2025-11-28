#!/bin/bash
# Deployment Monitoring Script
# Monitors Railway backend and Vercel frontend deployments

set -e

BACKEND_URL="${BACKEND_URL:-https://claude-code-projects-production.up.railway.app}"
FRONTEND_URL="${FRONTEND_URL:-}"  # Set this to your Vercel URL
CHECK_INTERVAL=5
MAX_ATTEMPTS=60

echo "=========================================="
echo "Deployment Monitoring"
echo "=========================================="
echo ""
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo "Check interval: ${CHECK_INTERVAL}s"
echo ""

# Function to check backend health
check_backend() {
    local attempt=$1
    echo "[$attempt/$MAX_ATTEMPTS] Checking backend health..."

    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$BACKEND_URL/health" 2>&1)
    HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
    BODY=$(echo "$RESPONSE" | grep -v "HTTP_STATUS")

    if [ "$HTTP_STATUS" == "200" ]; then
        echo "   ✅ Backend is healthy!"
        echo "   Response: $BODY"
        return 0
    else
        echo "   ⏳ Backend not ready yet (HTTP $HTTP_STATUS)"
        return 1
    fi
}

# Function to check frontend
check_frontend() {
    if [ -z "$FRONTEND_URL" ]; then
        echo "ℹ️  Frontend URL not set, skipping frontend check"
        return 0
    fi

    local attempt=$1
    echo "[$attempt/$MAX_ATTEMPTS] Checking frontend..."

    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>&1)

    if [ "$HTTP_STATUS" == "200" ]; then
        echo "   ✅ Frontend is accessible!"
        return 0
    else
        echo "   ⏳ Frontend not ready yet (HTTP $HTTP_STATUS)"
        return 1
    fi
}

# Function to check API version (to verify new code is deployed)
check_api_version() {
    echo "Checking if new code is deployed..."

    # Try to call the register endpoint to see if it exists (404 = old code, 400/422 = new code)
    RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d '{"test":"test"}' \
        -w "\nHTTP_STATUS:%{http_code}" 2>&1)

    HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

    if [ "$HTTP_STATUS" == "404" ]; then
        echo "   ⚠️  Old code still deployed (register endpoint not found)"
        return 1
    elif [ "$HTTP_STATUS" == "422" ] || [ "$HTTP_STATUS" == "400" ]; then
        echo "   ✅ New code deployed (register endpoint exists)"
        return 0
    else
        echo "   ⏳ Deployment status unclear (HTTP $HTTP_STATUS)"
        return 1
    fi
}

# Monitor backend deployment
echo "🔍 Monitoring backend deployment..."
echo ""

BACKEND_READY=false
for i in $(seq 1 $MAX_ATTEMPTS); do
    if check_backend $i && check_api_version; then
        BACKEND_READY=true
        break
    fi

    if [ $i -lt $MAX_ATTEMPTS ]; then
        sleep $CHECK_INTERVAL
    fi
done

echo ""

if [ "$BACKEND_READY" = false ]; then
    echo "❌ Backend deployment failed or timed out"
    exit 1
fi

# Monitor frontend deployment
if [ -n "$FRONTEND_URL" ]; then
    echo "🔍 Monitoring frontend deployment..."
    echo ""

    FRONTEND_READY=false
    for i in $(seq 1 $MAX_ATTEMPTS); do
        if check_frontend $i; then
            FRONTEND_READY=true
            break
        fi

        if [ $i -lt $MAX_ATTEMPTS ]; then
            sleep $CHECK_INTERVAL
        fi
    done

    echo ""

    if [ "$FRONTEND_READY" = false ]; then
        echo "❌ Frontend deployment failed or timed out"
        exit 1
    fi
fi

echo "=========================================="
echo "✅ Deployment monitoring complete!"
echo "=========================================="
echo ""
echo "Backend: ✅ Ready"
if [ -n "$FRONTEND_URL" ]; then
    echo "Frontend: ✅ Ready"
fi
echo ""
echo "Next steps:"
echo "  1. Seed test user: python scripts/seed_test_user.py"
echo "  2. Run auth tests: bash scripts/test_auth_flow.sh"
echo ""
