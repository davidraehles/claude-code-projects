#!/bin/bash

# Debugging script for meal plan generation feature
# Tests the API and frontend on the Vercel deployed version

BASE_URL="https://claude-code-projects.vercel.app"
API_URL="$BASE_URL/api/v1"

echo "🔍 Debugging Generate Meal Plan Feature"
echo "======================================"
echo ""

# Test 1: Check if API is accessible
echo "📊 Test 1: API Accessibility"
echo "----------------------------"
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/meal-plans")
echo "GET $API_URL/meal-plans"
echo "Status: $response"
if [ "$response" = "401" ] || [ "$response" = "403" ]; then
  echo "✓ API requires authentication (expected)"
elif [ "$response" = "200" ]; then
  echo "✓ API is accessible"
else
  echo "❌ Unexpected status code: $response"
fi
echo ""

# Test 2: Check recipes endpoint
echo "📊 Test 2: Recipes Endpoint"
echo "----------------------------"
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/recipes")
echo "GET $API_URL/recipes"
echo "Status: $response"
echo ""

# Test 3: Frontend page accessibility
echo "📊 Test 3: Frontend Page"
echo "------------------------"
page_status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/generate")
echo "GET $BASE_URL/generate"
echo "Status: $page_status"
if [ "$page_status" = "200" ]; then
  echo "✓ Page loads successfully"
else
  echo "❌ Page failed to load: $page_status"
fi
echo ""

# Test 4: Check for JavaScript files
echo "📊 Test 4: Assets and Resources"
echo "-------------------------------"
echo "Checking critical resources:"

# Check main HTML
html_check=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/generate")
echo "  - HTML page: $html_check"

# Check for Next.js build files
next_check=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/_next/static/")
echo "  - Next.js assets: $next_check"

echo ""
echo "✅ API and Frontend checks completed"
echo ""
echo "📋 Next steps:"
echo "  1. Run Playwright tests: npx playwright test e2e/meal-plan-generation.spec.ts --headed"
echo "  2. Check browser console for errors"
echo "  3. Verify backend is running on Railway"
echo "  4. Test meal plan generation manually"
echo ""
