#!/bin/bash
# Workflow Validation Script
# Validates GitHub Actions workflow files for syntax and best practices

set -e

echo "=== GitHub Actions Workflow Validator ==="
echo ""

WORKFLOWS_DIR=".github/workflows"
ERRORS=0
WARNINGS=0

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for required tools
echo "Checking for required tools..."

if ! command_exists yq; then
    echo -e "${YELLOW}Warning: yq not found. YAML syntax checking will be limited.${NC}"
    echo "Install with: pip install yq"
    WARNINGS=$((WARNINGS + 1))
fi

if ! command_exists actionlint; then
    echo -e "${YELLOW}Warning: actionlint not found. Advanced workflow validation will be skipped.${NC}"
    echo "Install with: https://github.com/rhysd/actionlint"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""

# Find all workflow files
WORKFLOW_FILES=$(find "$WORKFLOWS_DIR" -name "*.yml" -o -name "*.yaml" 2>/dev/null || true)

if [ -z "$WORKFLOW_FILES" ]; then
    echo -e "${RED}Error: No workflow files found in $WORKFLOWS_DIR${NC}"
    exit 1
fi

echo "Found workflow files:"
echo "$WORKFLOW_FILES"
echo ""

# Validate each workflow file
for workflow in $WORKFLOW_FILES; do
    echo "=== Validating: $workflow ==="

    # Check file exists and is readable
    if [ ! -r "$workflow" ]; then
        echo -e "${RED}Error: Cannot read file $workflow${NC}"
        ERRORS=$((ERRORS + 1))
        continue
    fi

    # Basic YAML syntax check
    if command_exists python3; then
        if ! python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
            echo -e "${RED}Error: Invalid YAML syntax in $workflow${NC}"
            ERRORS=$((ERRORS + 1))
            continue
        else
            echo -e "${GREEN}✓ Valid YAML syntax${NC}"
        fi
    fi

    # Check for required fields
    if ! grep -q "^name:" "$workflow"; then
        echo -e "${YELLOW}Warning: Missing 'name:' field in $workflow${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi

    if ! grep -q "^on:" "$workflow"; then
        echo -e "${RED}Error: Missing 'on:' trigger in $workflow${NC}"
        ERRORS=$((ERRORS + 1))
    fi

    if ! grep -q "^jobs:" "$workflow"; then
        echo -e "${RED}Error: Missing 'jobs:' section in $workflow${NC}"
        ERRORS=$((ERRORS + 1))
    fi

    # Check for best practices
    if ! grep -q "timeout-minutes:" "$workflow"; then
        echo -e "${YELLOW}Warning: No timeout specified in $workflow${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi

    # Check for cache usage
    if grep -q "setup-python" "$workflow" && ! grep -q "cache:" "$workflow"; then
        echo -e "${YELLOW}Warning: Python setup without caching in $workflow${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi

    if grep -q "setup-node" "$workflow" && ! grep -q "cache:" "$workflow"; then
        echo -e "${YELLOW}Warning: Node.js setup without caching in $workflow${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi

    # Run actionlint if available
    if command_exists actionlint; then
        if actionlint "$workflow" 2>/dev/null; then
            echo -e "${GREEN}✓ actionlint validation passed${NC}"
        else
            echo -e "${RED}Error: actionlint validation failed for $workflow${NC}"
            actionlint "$workflow" || true
            ERRORS=$((ERRORS + 1))
        fi
    fi

    echo ""
done

# Summary
echo "=== Validation Summary ==="
echo -e "Errors: ${RED}$ERRORS${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}Validation failed with $ERRORS error(s)${NC}"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}Validation completed with $WARNINGS warning(s)${NC}"
    exit 0
else
    echo -e "${GREEN}All workflows validated successfully!${NC}"
    exit 0
fi
