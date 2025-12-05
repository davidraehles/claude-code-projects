#!/usr/bin/env python3
"""
Test script for Workstream 1 components.

This script performs basic validation of the newly created infrastructure components:
1. Circuit Breaker
2. Security Headers Middleware
3. Rate Limit Middleware
4. Metrics integration

Run: python3 test_workstream1_components.py
"""

import sys
import ast
import os


def validate_python_file(filepath: str) -> tuple[bool, str]:
    """Validate a Python file for syntax errors."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        ast.parse(code)
        return True, f"✓ {filepath} - Syntax valid"
    except SyntaxError as e:
        return False, f"✗ {filepath} - Syntax error: {e}"
    except Exception as e:
        return False, f"✗ {filepath} - Error: {e}"


def check_file_exists(filepath: str) -> tuple[bool, str]:
    """Check if file exists."""
    if os.path.exists(filepath):
        return True, f"✓ {filepath} - File exists"
    return False, f"✗ {filepath} - File not found"


def main():
    """Run validation checks."""
    print("=" * 60)
    print("Workstream 1: Backend Infrastructure Enhancements")
    print("Component Validation")
    print("=" * 60)
    print()

    base_path = "/home/darae/claude-code-projects/backend"

    files_to_check = [
        "app/utils/circuit_breaker.py",
        "app/middleware/security_headers.py",
        "app/middleware/rate_limit_middleware.py",
        "app/monitoring/metrics.py",
        "app/services/knuspr_with_circuit_breaker.py",
        "app/main.py"
    ]

    all_passed = True

    print("1. File Existence Checks")
    print("-" * 60)
    for filepath in files_to_check:
        full_path = os.path.join(base_path, filepath)
        passed, message = check_file_exists(full_path)
        print(message)
        if not passed:
            all_passed = False
    print()

    print("2. Python Syntax Validation")
    print("-" * 60)
    for filepath in files_to_check:
        full_path = os.path.join(base_path, filepath)
        if os.path.exists(full_path):
            passed, message = validate_python_file(full_path)
            print(message)
            if not passed:
                all_passed = False
    print()

    print("3. Component Features Check")
    print("-" * 60)

    # Check circuit_breaker.py
    cb_path = os.path.join(base_path, "app/utils/circuit_breaker.py")
    with open(cb_path, 'r') as f:
        cb_content = f.read()

    checks = [
        ("CircuitState enum", "class CircuitState" in cb_content),
        ("CircuitBreaker class", "class CircuitBreaker" in cb_content),
        ("CircuitBreakerError", "class CircuitBreakerError" in cb_content),
        ("get_circuit_breaker factory", "def get_circuit_breaker" in cb_content),
        ("State transitions", "_transition_to_open" in cb_content and "_transition_to_half_open" in cb_content),
        ("Metrics collection", "def get_metrics" in cb_content),
    ]

    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"{status} Circuit Breaker: {check_name}")
        if not result:
            all_passed = False
    print()

    # Check security_headers.py
    sh_path = os.path.join(base_path, "app/middleware/security_headers.py")
    with open(sh_path, 'r') as f:
        sh_content = f.read()

    headers = [
        ("X-Content-Type-Options", "X-Content-Type-Options" in sh_content),
        ("X-Frame-Options", "X-Frame-Options" in sh_content),
        ("Content-Security-Policy", "Content-Security-Policy" in sh_content),
        ("Strict-Transport-Security", "Strict-Transport-Security" in sh_content),
        ("Permissions-Policy", "Permissions-Policy" in sh_content),
    ]

    for header_name, result in headers:
        status = "✓" if result else "✗"
        print(f"{status} Security Headers: {header_name}")
        if not result:
            all_passed = False
    print()

    # Check rate_limit_middleware.py
    rl_path = os.path.join(base_path, "app/middleware/rate_limit_middleware.py")
    with open(rl_path, 'r') as f:
        rl_content = f.read()

    features = [
        ("RateLimitMiddleware class", "class RateLimitMiddleware" in rl_content),
        ("IP extraction", "_extract_client_ip" in rl_content),
        ("429 response", "429" in rl_content),
        ("Retry-After header", "Retry-After" in rl_content),
        ("Endpoint-specific limits", "_configure_endpoint_limits" in rl_content),
    ]

    for feature_name, result in features:
        status = "✓" if result else "✗"
        print(f"{status} Rate Limit Middleware: {feature_name}")
        if not result:
            all_passed = False
    print()

    # Check metrics.py updates
    metrics_path = os.path.join(base_path, "app/monitoring/metrics.py")
    with open(metrics_path, 'r') as f:
        metrics_content = f.read()

    metrics = [
        ("Circuit breaker metrics", "circuit_breaker_state" in metrics_content),
        ("DB pool metrics", "db_connection_pool_active" in metrics_content),
        ("update_circuit_breaker_metrics", "def update_circuit_breaker_metrics" in metrics_content),
        ("update_db_pool_metrics", "def update_db_pool_metrics" in metrics_content),
    ]

    for metric_name, result in metrics:
        status = "✓" if result else "✗"
        print(f"{status} Metrics: {metric_name}")
        if not result:
            all_passed = False
    print()

    # Check main.py integration
    main_path = os.path.join(base_path, "app/main.py")
    with open(main_path, 'r') as f:
        main_content = f.read()

    integrations = [
        ("SecurityHeadersMiddleware registered", "SecurityHeadersMiddleware" in main_content),
        ("RateLimitMiddleware registered", "RateLimitMiddleware" in main_content),
        ("Graceful shutdown", "shutdown_event" in main_content),
        ("Metrics collection task", "collect_metrics_periodically" in main_content),
        ("DB pool metrics", "update_db_pool_metrics" in main_content),
        ("Circuit breaker metrics", "update_circuit_breaker_metrics" in main_content),
    ]

    for integration_name, result in integrations:
        status = "✓" if result else "✗"
        print(f"{status} Main.py Integration: {integration_name}")
        if not result:
            all_passed = False
    print()

    print("=" * 60)
    if all_passed:
        print("✓ ALL CHECKS PASSED")
        print("=" * 60)
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
