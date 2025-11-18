#!/bin/bash
# Watch for Railway deployment to complete

echo "Starting deployment monitoring..."
echo "Pushed at: $(date)"
echo ""
echo "Will check every 20 seconds for 3 minutes..."
echo ""

for i in {1..9}; do
  echo "Check $i/9 - $(date '+%H:%M:%S')"

  RESULT=$(curl -s -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"check${i}@test.com\",\"password\":\"testpassword123\",\"country\":\"US\"}" 2>&1)

  if echo "$RESULT" | grep -q "password cannot be longer than 72 bytes"; then
    echo "  ⏳ Old code (bcrypt bug still present)"
  elif echo "$RESULT" | grep -q "already registered"; then
    echo "  ✅ NEW CODE DEPLOYED! User already exists"
    echo ""
    echo "Deployment successful!"
    exit 0
  elif echo "$RESULT" | grep -q "access_token"; then
    echo "  ✅ NEW CODE DEPLOYED! Registration successful"
    echo "  Full response:"
    echo "$RESULT" | head -3
    echo ""
    echo "Deployment successful!"
    exit 0
  elif echo "$RESULT" | grep -q "Internal server error"; then
    ERROR_MSG=$(echo "$RESULT" | grep -o '"message":"[^"]*' | cut -d'"' -f4)
    echo "  ⏳ Still deploying or different error"
    echo "  Error: $ERROR_MSG"
  else
    echo "  ℹ️  Response: $(echo "$RESULT" | head -1)"
  fi

  if [ $i -lt 9 ]; then
    sleep 20
  fi
done

echo ""
echo "Monitoring timed out at: $(date '+%H:%M:%S')"
echo "Check Railway dashboard for deployment status"
