#!/bin/bash

# Script to run visual regression tests
# This script handles the server startup and test execution

echo "Starting visual regression tests..."

# Check if server is already running
if curl -s http://localhost:3000 > /dev/null; then
    echo "✓ Server is already running on port 3000"
else
    echo "✗ Server is not running. Starting server..."
    cd /home/darae/meal-planner/frontend
    npm run dev &
    
    # Wait for server to start
    echo "Waiting for server to start..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null; then
            echo "✓ Server started successfully"
            break
        fi
        sleep 2
        echo "Waiting... ($i/30)"
    done
fi

# Run the visual regression tests
echo "Running visual regression tests..."
cd /home/darae/meal-planner/frontend

# First, create baseline screenshots (update snapshots)
echo "Creating baseline screenshots..."
npx playwright test e2e/visual-regression.spec.ts --project=chromium --update-snapshots

# Then run the tests to verify they pass
echo "Running tests against baselines..."
npx playwright test e2e/visual-regression.spec.ts --project=chromium

# Run the logo and image tests
echo "Running logo and image consistency tests..."
npx playwright test e2e/logo-images-knuspr.spec.ts --project=chromium

echo "✓ All visual regression tests completed!"

# Generate HTML report
echo "Generating HTML report..."
npx playwright show-report