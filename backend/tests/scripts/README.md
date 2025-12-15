# Test Scripts

Collection of shell scripts for testing various features of the meal planner.

## Available Scripts

### test-knuspr-cheese.sh
Tests Knuspr integration by adding cheese products to cart.
```bash
./test-knuspr-cheese.sh
```

### test-railway-integration.sh
Tests Railway deployment integration and connectivity.
```bash
./test-railway-integration.sh
```

### test_feature4_implementation.sh
Tests Feature 4 implementation (specific feature validation).
```bash
./test_feature4_implementation.sh
```

### validate-phase1.sh
Validates Phase 1 deployment completeness.
```bash
./validate-phase1.sh
```

## Usage

All scripts should be run from the project root:
```bash
cd /home/darae/meal-planner
backend/tests/scripts/test-knuspr-cheese.sh
```

Or make them executable and run directly:
```bash
chmod +x backend/tests/scripts/*.sh
backend/tests/scripts/test-knuspr-cheese.sh
```
