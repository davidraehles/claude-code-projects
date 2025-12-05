# Runbook Collection

## Overview

This document contains operational runbooks for common incidents and alerts in the AI Meal Planner application.

---

## Table of Contents

1. [High Error Rate](#1-high-error-rate)
2. [Service Down](#2-service-down)
3. [Database Connection Issues](#3-database-connection-issues)
4. [High Latency](#4-high-latency)
5. [Database Slow Queries](#5-database-slow-queries)
6. [Circuit Breaker Open](#6-circuit-breaker-open)
7. [Memory Issues](#7-memory-issues)
8. [Disk Space Critical](#8-disk-space-critical)
9. [Low Cart Completion Rate](#9-low-cart-completion-rate)
10. [External API Failure](#10-external-api-failure)
11. [Deployment Failure](#11-deployment-failure)
12. [Rate Limit Exceeded](#12-rate-limit-exceeded)

---

## 1. High Error Rate

**Alert Name:** `HighErrorRate`
**Severity:** Critical
**Threshold:** Error rate > 5% of total requests

### Symptoms
- Increased 5xx responses
- User complaints about errors
- Error rate gauge in red zone

### Investigation Steps

1. **Check API Health Dashboard**
   - Navigate to: http://localhost:3000/d/api-health-v1
   - Identify affected endpoints
   - Check error distribution (4xx vs 5xx)

2. **Review Recent Changes**
   ```bash
   # Check recent deployments
   docker ps -a --filter "label=service=api" --format "{{.CreatedAt}} {{.Status}}"

   # Check application logs
   docker logs recipe-api --since 1h | grep ERROR
   ```

3. **Analyze Error Patterns**
   - Open Loki: http://localhost:3000/explore
   - Query: `{container="recipe-api"} |= "ERROR"`
   - Look for common error messages

4. **Check Distributed Traces**
   - Open Jaeger: http://localhost:16686
   - Filter by: service=ai-meal-planner-api, tags=error:true
   - Examine failed request traces

### Resolution

**If deployment-related:**
```bash
# Rollback to previous version
cd backend
git log -1  # Check current commit
git checkout <previous-stable-commit>
docker-compose up -d --build api
```

**If database-related:**
- See [Database Connection Issues](#3-database-connection-issues)

**If external API-related:**
- See [External API Failure](#10-external-api-failure)

### Post-Incident
- Document root cause
- Update monitoring if needed
- Create Jira ticket for fix
- Post mortem if service impact > 15 min

---

## 2. Service Down

**Alert Name:** `ServiceDown`
**Severity:** Critical
**Threshold:** Service unreachable for 1 minute

### Symptoms
- Service returns no response
- Health check fails
- All requests timeout

### Investigation Steps

1. **Check Container Status**
   ```bash
   # Check if container is running
   docker ps | grep recipe-api

   # If not running, check why
   docker ps -a | grep recipe-api
   docker logs recipe-api --tail 100
   ```

2. **Check Resource Usage**
   ```bash
   # Check if out of memory/CPU
   docker stats recipe-api --no-stream
   ```

3. **Check Dependencies**
   ```bash
   # Verify database is up
   docker exec recipe-postgres pg_isready

   # Verify Redis is up
   docker exec recipe-redis redis-cli ping
   ```

### Resolution

**If container crashed:**
```bash
# Restart container
docker-compose restart api

# If restart fails, rebuild
docker-compose up -d --build api
```

**If out of resources:**
```bash
# Increase container limits in docker-compose.yml
# Add under api service:
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '2'

docker-compose up -d api
```

**If dependency issue:**
- Resolve dependency first (database, Redis)
- Then restart API service

### Post-Incident
- Review resource allocation
- Add preemptive scaling alerts
- Document incident timeline

---

## 3. Database Connection Issues

**Alert Name:** `DatabaseConnectionError`
**Severity:** Critical
**Threshold:** Connection failures > 10% for 2 minutes

### Symptoms
- Database connection timeouts
- Connection pool exhausted
- SQLAlchemy errors in logs

### Investigation Steps

1. **Check Database Health**
   ```bash
   # Check if database is accepting connections
   docker exec recipe-postgres pg_isready -U postgres

   # Check active connections
   docker exec recipe-postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

   # Check max connections
   docker exec recipe-postgres psql -U postgres -c "SHOW max_connections;"
   ```

2. **Review Connection Pool**
   - Dashboard: http://localhost:3000/d/database-performance-v1
   - Check: Connection Pool Usage panel
   - Look for pool exhaustion

3. **Check for Long-Running Queries**
   ```bash
   docker exec recipe-postgres psql -U postgres -c "
   SELECT pid, now() - pg_stat_activity.query_start AS duration, query
   FROM pg_stat_activity
   WHERE state = 'active'
   ORDER BY duration DESC;
   "
   ```

### Resolution

**If pool exhausted:**
```python
# Update backend/app/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,      # Increase from 10
    max_overflow=40,   # Increase from 20
)
```

**If long-running queries:**
```bash
# Kill specific query
docker exec recipe-postgres psql -U postgres -c "SELECT pg_terminate_backend(<PID>);"
```

**If database down:**
```bash
# Restart database
docker-compose restart db

# Check logs for errors
docker logs recipe-postgres --tail 100
```

### Post-Incident
- Review query performance
- Optimize slow queries
- Adjust connection pool settings
- Add connection pool monitoring

---

## 4. High Latency

**Alert Name:** `HighLatency`
**Severity:** High
**Threshold:** P99 latency > 2 seconds for 5 minutes

### Symptoms
- Slow API responses
- User complaints about performance
- Increased request timeouts

### Investigation Steps

1. **Identify Slow Endpoints**
   - Dashboard: http://localhost:3000/d/api-health-v1
   - Panel: P99 Latency by Endpoint
   - Sort by highest latency

2. **Check Distributed Traces**
   - Jaeger: http://localhost:16686
   - Find slow requests (> 2s)
   - Analyze span timing
   - Identify bottlenecks

3. **Check Resource Usage**
   - Dashboard: http://localhost:3000/d/infrastructure-v1
   - CPU usage by container
   - Memory usage
   - Disk I/O

4. **Database Query Analysis**
   - Dashboard: http://localhost:3000/d/database-performance-v1
   - Check slow queries panel
   - Review query latency

### Resolution

**If database bottleneck:**
- Add indexes to slow queries
- Optimize query logic
- Implement caching

**If external API bottleneck:**
- Check circuit breaker status
- Implement request timeouts
- Add caching layer

**If resource constrained:**
```bash
# Scale up resources
docker-compose up -d --scale api=2
```

### Post-Incident
- Performance testing
- Code optimization
- Caching strategy review
- Load testing

---

## 5. Database Slow Queries

**Alert Name:** `DatabaseSlowQueries`
**Severity:** High
**Threshold:** > 10 queries taking > 1 second in 5 minutes

### Investigation Steps

1. **Identify Slow Queries**
   ```bash
   docker exec recipe-postgres psql -U postgres recipe_app -c "
   SELECT query, calls, total_exec_time, mean_exec_time
   FROM pg_stat_statements
   WHERE mean_exec_time > 1000
   ORDER BY mean_exec_time DESC
   LIMIT 10;
   "
   ```

2. **Analyze Query Plans**
   ```bash
   docker exec recipe-postgres psql -U postgres recipe_app -c "
   EXPLAIN ANALYZE <slow-query>;
   "
   ```

3. **Check Missing Indexes**
   ```bash
   docker exec recipe-postgres psql -U postgres recipe_app -c "
   SELECT schemaname, tablename, attname, n_distinct, correlation
   FROM pg_stats
   WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
   AND tablename IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public');
   "
   ```

### Resolution

**Add indexes:**
```sql
-- Example: Add index on frequently queried column
CREATE INDEX idx_recipes_user_id ON recipes(user_id);
CREATE INDEX idx_meal_plans_created_at ON meal_plans(created_at DESC);
```

**Optimize query:**
```python
# Before: N+1 query problem
recipes = await db.execute(select(Recipe))
for recipe in recipes:
    ingredients = await db.execute(select(Ingredient).where(Ingredient.recipe_id == recipe.id))

# After: Join and eager load
recipes = await db.execute(
    select(Recipe).options(selectinload(Recipe.ingredients))
)
```

**Enable query result caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_popular_recipes():
    # Cache frequently accessed data
    ...
```

### Post-Incident
- Regular query performance reviews
- Index maintenance schedule
- Query optimization guidelines

---

## 6. Circuit Breaker Open

**Alert Name:** `CircuitBreakerOpen`
**Severity:** High
**Threshold:** Circuit breaker open for > 5 minutes

### Symptoms
- External API calls failing
- Circuit breaker in open state
- Degraded functionality

### Investigation Steps

1. **Check Circuit Breaker Status**
   - Dashboard: http://localhost:3000/d/application-internals-v1
   - Panel: Circuit Breaker Status
   - Identify affected service (Knuspr, etc.)

2. **Check External Service Health**
   ```bash
   # Test Knuspr API
   curl -I https://api.knuspr.de/health

   # Check response time
   time curl https://api.knuspr.de/health
   ```

3. **Review Recent Failures**
   - Logs: `docker logs recipe-api | grep "CircuitBreaker"`
   - Check failure count
   - Review error patterns

### Resolution

**If external service is down:**
- Enable fallback mode
- Notify users of degraded functionality
- Monitor external service status

**If rate limiting:**
- Reduce request rate
- Implement backoff strategy
- Request rate limit increase

**Manual circuit reset:**
```python
# Via API endpoint (if implemented)
POST /api/v1/admin/circuit-breaker/reset
{
  "service": "knuspr"
}
```

**Wait for automatic recovery:**
- Circuit breaker will attempt to close after timeout
- Monitor success rate
- Gradual recovery expected

### Post-Incident
- Review circuit breaker thresholds
- Implement better fallbacks
- Add external service monitoring
- Communication with external service provider

---

## 7. Memory Issues

**Alert Name:** `HighMemoryUsage`
**Severity:** High
**Threshold:** Memory usage > 90% for 5 minutes

### Investigation Steps

1. **Check Memory Usage**
   ```bash
   # Container memory
   docker stats recipe-api --no-stream

   # System memory
   free -h
   ```

2. **Identify Memory Leaks**
   ```bash
   # Check for growing memory over time
   docker stats recipe-api

   # Application profiling (if enabled)
   # Use memory profiler or tracemalloc
   ```

3. **Review Application Logs**
   ```bash
   docker logs recipe-api | grep -i "memory\|oom"
   ```

### Resolution

**Restart container (immediate):**
```bash
docker-compose restart api
```

**Increase memory limit:**
```yaml
# docker-compose.yml
api:
  deploy:
    resources:
      limits:
        memory: 2G  # Increase from 1G
```

**Fix memory leak (long-term):**
- Profile application with memory profiler
- Identify leak source
- Fix and deploy

### Post-Incident
- Memory profiling
- Leak detection automation
- Regular memory monitoring
- Resource planning

---

## 8. Disk Space Critical

**Alert Name:** `DiskSpaceCritical`
**Severity:** Critical
**Threshold:** Disk usage > 90%

### Investigation Steps

1. **Check Disk Usage**
   ```bash
   # Overall disk usage
   df -h

   # Docker disk usage
   docker system df
   ```

2. **Identify Large Files/Volumes**
   ```bash
   # Find large directories
   du -sh /* | sort -hr | head -10

   # Check Docker volumes
   docker volume ls
   docker system df -v
   ```

### Resolution

**Clean Docker resources:**
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused build cache
docker builder prune

# Full cleanup (careful!)
docker system prune -a --volumes
```

**Clean application logs:**
```bash
# Rotate logs
docker-compose exec api sh -c "truncate -s 0 /var/log/app/*.log"

# Configure log rotation in docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

**Clean database backups:**
```bash
# Remove old backups (keep last 7 days)
find /backups -name "*.sql.gz" -mtime +7 -delete
```

### Post-Incident
- Implement automated cleanup
- Add disk monitoring
- Log rotation configuration
- Storage capacity planning

---

## 9. Low Cart Completion Rate

**Alert Name:** `LowCartCompletionRate`
**Severity:** Medium
**Threshold:** Completion rate < 50% for 1 hour

### Investigation Steps

1. **Check Business Metrics**
   - Dashboard: http://localhost:3000/d/business-metrics-v1
   - Panel: Cart Completion Rate
   - Review trend over time

2. **Analyze User Flow**
   - Jaeger: http://localhost:16686
   - Search for cart creation traces
   - Identify where users drop off

3. **Check for Errors**
   ```bash
   # Cart-related errors
   docker logs recipe-api | grep -i "cart\|grocery" | grep ERROR
   ```

4. **Verify Knuspr Integration**
   - Dashboard: http://localhost:3000/d/application-internals-v1
   - Check Knuspr API success rate
   - Review circuit breaker status

### Resolution

**If integration issues:**
- Check Knuspr API health
- Review rate limits
- Verify API credentials

**If UX issues:**
- Review user feedback
- Check frontend error logs
- A/B testing if needed

**If performance issues:**
- Optimize cart generation
- Reduce latency
- Improve caching

### Post-Incident
- User experience review
- Frontend/backend coordination
- Product team feedback
- Conversion optimization

---

## 10. External API Failure

**Alert Name:** `ExternalAPIFailure`
**Severity:** High
**Threshold:** > 20% failure rate for external API calls

### Investigation Steps

1. **Identify Failing Service**
   - Dashboard: http://localhost:3000/d/application-internals-v1
   - Check external API metrics

2. **Test API Directly**
   ```bash
   # Test Knuspr API
   curl -X GET https://api.knuspr.de/v1/products \
     -H "Authorization: Bearer $TOKEN"

   # Check status page
   curl https://status.knuspr.de
   ```

3. **Review Error Patterns**
   ```bash
   docker logs recipe-api | grep "knuspr\|external" | grep ERROR
   ```

### Resolution

**If service is down:**
- Enable fallback mode
- Cache last known good data
- Notify users

**If authentication issue:**
- Refresh API tokens
- Verify credentials
- Check token expiration

**If rate limiting:**
- Implement backoff
- Reduce request frequency
- Request limit increase

### Post-Incident
- SLA review with provider
- Implement better fallbacks
- Add external monitoring
- Disaster recovery plan

---

## 11. Deployment Failure

**Alert Name:** `DeploymentFailed`
**Severity:** High
**Threshold:** Deployment health check fails

### Investigation Steps

1. **Check Deployment Status**
   ```bash
   # Check container status
   docker ps -a | grep recipe-api

   # Check build logs
   docker-compose logs api
   ```

2. **Review Health Checks**
   ```bash
   # Test health endpoint
   curl http://localhost:8000/health

   # Check startup logs
   docker logs recipe-api --tail 100
   ```

3. **Verify Dependencies**
   ```bash
   # Database migration status
   docker-compose exec api alembic current

   # Check Redis connection
   docker-compose exec api python -c "import redis; r=redis.Redis(host='redis'); print(r.ping())"
   ```

### Resolution

**If build failure:**
```bash
# Rebuild with no cache
docker-compose build --no-cache api
docker-compose up -d api
```

**If migration failure:**
```bash
# Check migration status
docker-compose exec api alembic current
docker-compose exec api alembic history

# Rollback migration if needed
docker-compose exec api alembic downgrade -1
```

**If health check failure:**
- Review health check implementation
- Increase timeout
- Fix underlying issue

**Rollback deployment:**
```bash
git checkout <previous-stable-commit>
docker-compose up -d --build api
```

### Post-Incident
- Improve CI/CD checks
- Add pre-deployment testing
- Review rollback procedures
- Deployment checklist update

---

## 12. Rate Limit Exceeded

**Alert Name:** `RateLimitExceeded`
**Severity:** Medium
**Threshold:** > 100 rate limit violations per hour

### Investigation Steps

1. **Identify Source**
   - Dashboard: http://localhost:3000/d/api-health-v1
   - Panel: Rate Limit Violations
   - Check by tier/user

2. **Check User Activity**
   ```bash
   # Query rate limit logs
   docker logs recipe-api | grep "RateLimit" | tail -100
   ```

3. **Analyze Traffic Patterns**
   - Unusual spike?
   - Legitimate traffic?
   - Potential abuse?

### Resolution

**If legitimate traffic:**
- Increase rate limits temporarily
- Consider tier upgrade for user
- Add caching to reduce requests

**If abuse/bot traffic:**
- Block offending IPs
- Implement CAPTCHA
- Review authentication

**Adjust rate limits:**
```python
# backend/app/utils/rate_limit.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]  # Adjust as needed
)
```

### Post-Incident
- Review rate limit strategy
- User communication
- Bot detection improvement
- Tier structure review

---

## Emergency Contacts

- **On-Call Engineer:** PagerDuty escalation
- **Database Team:** #database-team
- **DevOps Team:** #devops
- **Security Team:** #security
- **Product Team:** #product

## Support Resources

- **Documentation:** `/docs`
- **Monitoring Guide:** `/infrastructure/ADVANCED_MONITORING_GUIDE.md`
- **Architecture Docs:** `/docs/ARCHITECTURE.md`
- **Slack Channels:** #alerts, #incident-response

---

**Last Updated:** 2025-12-05
**Maintained By:** SRE Team
**Review Frequency:** Monthly
