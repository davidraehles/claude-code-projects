"""
Phase 5: Load Testing (T212)

Tests to verify the system can handle 10+ concurrent users under load.

Uses multiple strategies:
1. Concurrent requests simulation
2. Request rate testing
3. Resource utilization monitoring
4. Error recovery under load
"""

import asyncio
import time
import threading
import concurrent.futures
from typing import List, Tuple
import statistics

import pytest
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, '/home/darae/claude-code-projects')

from src.main import app
from src.services.auth import create_access_token, hash_password


client = TestClient(app)


def generate_test_auth():
    """Generate authentication headers for a test user"""
    # Use a pre-existing or create new test user
    email = f"loadtest-{int(time.time() * 1000)}-{threading.get_ident()}@example.com"
    password = "LoadTestPassword123"

    # Try to signup
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "password": password,
            "country": "nl"
        }
    )

    # If signup fails (duplicate), try login
    if response.status_code not in [200, 201]:
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": email,
                "password": password
            }
        )

    if response.status_code in [200, 201]:
        data = response.json()
        token = data.get("access_token")
        return {"Authorization": f"Bearer {token}"}
    else:
        # Fallback: create token manually
        return {"Authorization": f"Bearer fake-token-{threading.get_ident()}"}


class TestPhase5LoadRecipeSearch:
    """T212: Load test recipe search with multiple concurrent users"""

    def test_10_concurrent_recipe_searches(self):
        """Test 10 concurrent users searching recipes"""
        results: List[Tuple[int, float]] = []

        def search_recipe(user_id: int) -> Tuple[int, float]:
            headers = generate_test_auth()
            start_time = time.time()

            response = client.get(
                "/api/v1/recipes",
                headers=headers,
                params={"search": "tomato", "limit": 20}
            )

            duration = time.time() - start_time
            return response.status_code, duration

        # Run 10 concurrent searches
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(search_recipe, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Verify results
        statuses = [r[0] for r in results]
        durations = [r[1] for r in results]

        print(f"\n10 Concurrent Recipe Searches:")
        print(f"  Success rate: {sum(1 for s in statuses if s == 200)}/10")
        print(f"  Response times: min={min(durations)*1000:.0f}ms, max={max(durations)*1000:.0f}ms, avg={statistics.mean(durations)*1000:.0f}ms")

        # At least 8/10 should succeed
        assert sum(1 for s in statuses if s == 200) >= 8

        # Average response time should be reasonable
        assert statistics.mean(durations) < 2.0  # 2 seconds

    def test_20_concurrent_recipe_searches(self):
        """Test 20 concurrent users searching recipes"""
        results: List[Tuple[int, float]] = []

        def search_recipe(user_id: int) -> Tuple[int, float]:
            headers = generate_test_auth()
            start_time = time.time()

            response = client.get(
                "/api/v1/recipes",
                headers=headers,
                params={"search": "pasta", "limit": 10}
            )

            duration = time.time() - start_time
            return response.status_code, duration

        # Run 20 concurrent searches
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(search_recipe, i) for i in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        statuses = [r[0] for r in results]
        durations = [r[1] for r in results]

        print(f"\n20 Concurrent Recipe Searches:")
        print(f"  Success rate: {sum(1 for s in statuses if s == 200)}/20")
        print(f"  Response times: min={min(durations)*1000:.0f}ms, max={max(durations)*1000:.0f}ms, avg={statistics.mean(durations)*1000:.0f}ms")

        # At least 15/20 should succeed
        assert sum(1 for s in statuses if s == 200) >= 15


class TestPhase5LoadMealPlanGeneration:
    """T212: Load test meal plan generation"""

    def test_5_concurrent_meal_plan_generations(self):
        """Test 5 concurrent users generating meal plans"""
        results: List[Tuple[int, float]] = []

        def generate_meal_plan(user_id: int) -> Tuple[int, float]:
            headers = generate_test_auth()
            start_time = time.time()

            response = client.post(
                "/api/v1/mealplans",
                headers=headers,
                json={
                    "days": 3,
                    "servings": 2,
                    "dietary_preferences": [],
                    "excluded_ingredients": [],
                    "preferred_recipes": []
                }
            )

            duration = time.time() - start_time
            return response.status_code, duration

        # Run 5 concurrent meal plan generations
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_meal_plan, i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        statuses = [r[0] for r in results]
        durations = [r[1] for r in results]

        print(f"\n5 Concurrent Meal Plan Generations:")
        print(f"  Success rate: {sum(1 for s in statuses if s in [200, 201, 202])}/5")
        print(f"  Response times: min={min(durations)*1000:.0f}ms, max={max(durations)*1000:.0f}ms, avg={statistics.mean(durations)*1000:.0f}ms")

        # At least 3/5 should succeed
        assert sum(1 for s in statuses if s in [200, 201, 202]) >= 3


class TestPhase5LoadMixedWorkload:
    """T212: Load test mixed workloads"""

    def test_mixed_workload_10_users(self):
        """Test 10 concurrent users with mixed operations"""
        results: List[Tuple[str, int, float]] = []

        def user_workflow(user_id: int):
            headers = generate_test_auth()
            operations = []

            # Operation 1: Search recipes
            start = time.time()
            response = client.get(
                "/api/v1/recipes",
                headers=headers,
                params={"search": "vegetable"}
            )
            operations.append(("recipe_search", response.status_code, time.time() - start))

            # Operation 2: Get user preferences
            start = time.time()
            response = client.get(
                "/api/v1/users/preferences",
                headers=headers
            )
            operations.append(("preferences_fetch", response.status_code, time.time() - start))

            # Operation 3: Get ingredient info
            start = time.time()
            response = client.get(
                "/api/v1/ingredients/tomato",
                headers=headers
            )
            operations.append(("ingredient_lookup", response.status_code, time.time() - start))

            return operations

        # Run 10 concurrent users with mixed workload
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(user_workflow, i) for i in range(10)]
            all_results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Flatten results
        for user_ops in all_results:
            results.extend(user_ops)

        # Analyze by operation type
        operation_types = {}
        for op_name, status, duration in results:
            if op_name not in operation_types:
                operation_types[op_name] = {"statuses": [], "durations": []}
            operation_types[op_name]["statuses"].append(status)
            operation_types[op_name]["durations"].append(duration)

        print(f"\n10 Users Mixed Workload (30 total operations):")
        for op_name, data in operation_types.items():
            success_count = sum(1 for s in data["statuses"] if s in [200, 201, 202])
            avg_time = statistics.mean(data["durations"]) * 1000
            print(f"  {op_name}: {success_count}/10 success, avg {avg_time:.0f}ms")

        # Overall success rate should be >80%
        total_success = sum(1 for op, status, _ in results if status in [200, 201, 202])
        assert total_success >= len(results) * 0.8


class TestPhase5LoadAPIEndpoints:
    """T212: Load test various API endpoints"""

    def test_concurrent_user_profile_access(self):
        """Test concurrent access to user profiles"""
        results: List[Tuple[int, float]] = []

        def get_profile(user_id: int) -> Tuple[int, float]:
            headers = generate_test_auth()
            start_time = time.time()

            response = client.get(
                "/api/v1/users/me",
                headers=headers
            )

            duration = time.time() - start_time
            return response.status_code, duration

        # 10 concurrent profile accesses
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_profile, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        statuses = [r[0] for r in results]
        durations = [r[1] for r in results]

        print(f"\n10 Concurrent User Profile Accesses:")
        print(f"  Success rate: {sum(1 for s in statuses if s == 200)}/10")
        print(f"  Response times: avg={statistics.mean(durations)*1000:.0f}ms")

        assert sum(1 for s in statuses if s == 200) >= 8

    def test_concurrent_cart_operations(self):
        """Test concurrent cart operations"""
        results: List[Tuple[int, float]] = []

        def cart_operation(user_id: int) -> Tuple[int, float]:
            headers = generate_test_auth()
            start_time = time.time()

            response = client.get(
                "/api/v1/carts",
                headers=headers
            )

            duration = time.time() - start_time
            return response.status_code, duration

        # 10 concurrent cart accesses
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(cart_operation, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        statuses = [r[0] for r in results]

        print(f"\n10 Concurrent Cart Operations:")
        print(f"  Success rate: {sum(1 for s in statuses if s == 200)}/10")

        assert sum(1 for s in statuses if s == 200) >= 8


class TestPhase5LoadSustained:
    """T212: Sustained load testing"""

    def test_sustained_load_30_seconds(self):
        """Test sustained load for 30 seconds"""
        start_time = time.time()
        request_count = 0
        success_count = 0
        error_count = 0
        durations = []

        def single_request():
            nonlocal request_count, success_count, error_count
            headers = generate_test_auth()
            req_start = time.time()

            response = client.get(
                "/api/v1/recipes",
                headers=headers,
                params={"limit": 5}
            )

            duration = time.time() - req_start
            request_count += 1
            durations.append(duration)

            if response.status_code == 200:
                success_count += 1
            else:
                error_count += 1

        # Run for 30 seconds with 3 concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            while time.time() - start_time < 30:
                futures.append(executor.submit(single_request))
                time.sleep(0.1)  # 10 requests per second across 3 workers

            # Wait for remaining futures
            concurrent.futures.wait(futures)

        elapsed = time.time() - start_time

        print(f"\n30-Second Sustained Load Test:")
        print(f"  Duration: {elapsed:.1f}s")
        print(f"  Total requests: {request_count}")
        print(f"  Successful: {success_count}")
        print(f"  Failed: {error_count}")
        print(f"  Success rate: {success_count/request_count*100:.1f}%")
        print(f"  Throughput: {request_count/elapsed:.1f} req/s")
        print(f"  Response times: min={min(durations)*1000:.0f}ms, avg={statistics.mean(durations)*1000:.0f}ms, max={max(durations)*1000:.0f}ms")

        # Should maintain >80% success rate
        assert success_count / request_count > 0.8


class TestPhase5LoadStressTest:
    """T212: Stress testing"""

    def test_escalating_load(self):
        """Test system under escalating load"""
        results = {}

        for num_users in [5, 10, 15, 20]:
            user_results = []

            def user_request(user_id: int):
                headers = generate_test_auth()
                start = time.time()

                response = client.get(
                    "/api/v1/recipes",
                    headers=headers,
                    params={"limit": 10}
                )

                return response.status_code, time.time() - start

            with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
                futures = [executor.submit(user_request, i) for i in range(num_users)]
                user_results = [f.result() for f in concurrent.futures.as_completed(futures)]

            statuses = [r[0] for r in user_results]
            durations = [r[1] for r in user_results]
            success_rate = sum(1 for s in statuses if s == 200) / num_users

            results[num_users] = {
                "success_rate": success_rate,
                "avg_duration": statistics.mean(durations)
            }

            print(f"\nLoad test with {num_users} users:")
            print(f"  Success rate: {success_rate*100:.1f}%")
            print(f"  Avg response time: {statistics.mean(durations)*1000:.0f}ms")

        # System should maintain reasonable performance up to 20 users
        # At 20 users, should still have >70% success rate
        assert results[20]["success_rate"] >= 0.7


class TestPhase5LoadErrorRecovery:
    """T212: Error handling under load"""

    def test_recovery_from_transient_failures(self):
        """Test system recovery from transient failures"""
        success_sequence = []

        def request_with_retry(max_retries=3):
            headers = generate_test_auth()

            for attempt in range(max_retries):
                response = client.get(
                    "/api/v1/recipes",
                    headers=headers,
                    params={"limit": 10}
                )

                if response.status_code == 200:
                    return True

                if attempt < max_retries - 1:
                    time.sleep(0.1 * (2 ** attempt))  # Exponential backoff

            return False

        # Test 10 concurrent requests with retry logic
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(request_with_retry) for _ in range(10)]
            success_sequence = [f.result() for f in concurrent.futures.as_completed(futures)]

        success_rate = sum(success_sequence) / len(success_sequence)
        print(f"\nError Recovery Test (with retries):")
        print(f"  Success rate: {success_rate*100:.1f}%")

        # Should recover most failures
        assert success_rate >= 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-k", "test_"])
