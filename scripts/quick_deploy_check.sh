#!/bin/bash
# Quick deployment check for Railway

echo "Checking Railway deployment status..."

for i in {1..5}; do
  echo ""
  echo "Attempt $i/5 - $(date)"
  RESULT=$(curl -s -X POST https://claude-code-projects-production.up.railway.app/api/v1/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"test123","country":"US"}' 2>&1)

  if echo "$RESULT" | grep -q "password cannot be longer than 72 bytes"; then
    echo "  ⏳ Old code still deployed (password hashing bug present)"
  elif echo "$RESULT" | grep -q "already registered"; then
    echo "  ✅ NEW CODE DEPLOYED! (User already exists - expected behavior)"
    exit 0
  elif echo "$RESULT" | grep -q "access_token"; then
    echo "  ✅ NEW CODE DEPLOYED! (Registration successful)"
    exit 0
  else
    echo "  Response: $RESULT"
  fi

  if [ $i -lt 5 ]; then
    echo "  Waiting 15 seconds before next check..."
    sleep 15
  fi
done

echo ""
echo "⚠️  Deployment may still be in progress. Check Railway dashboard."
