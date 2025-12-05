# Production Deployment Checklist

This checklist ensures all security, monitoring, and operational requirements are met before deploying to production.

## Security Configuration

### Authentication & Authorization
- [ ] Generate strong `SECRET_KEY` (min 32 characters)
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] Generate strong `JWT_SECRET_KEY` (min 32 characters)
- [ ] Verify JWT expiration time is appropriate for your use case
- [ ] Review and restrict API rate limits if needed

### CORS Configuration
- [ ] **CRITICAL**: Set `CORS_ORIGINS` to specific domain(s) - NO wildcards!
  ```bash
  # Example (comma-separated list):
  CORS_ORIGINS=https://app.example.com,https://www.example.com
  ```
- [ ] Verify frontend domain is included in CORS_ORIGINS
- [ ] Verify NO wildcard (`*`) is present in CORS_ORIGINS
- [ ] Test CORS with actual frontend domain

### Grafana Monitoring
- [ ] **CRITICAL**: Change `GRAFANA_ADMIN_USER` from default
- [ ] **CRITICAL**: Change `GRAFANA_ADMIN_PASSWORD` from default (use strong password)
- [ ] Restrict network access to Grafana (port 3000)
- [ ] Enable HTTPS for Grafana (reverse proxy recommended)

### Database Security
- [ ] Use strong `DB_PASSWORD` (min 16 characters)
- [ ] Restrict database network access (firewall rules)
- [ ] Enable SSL/TLS for database connections
- [ ] Review database user permissions (least privilege)

### CSRF Protection
- [ ] Verify CSRF middleware is enabled in main.py
- [ ] Configure frontend to send X-CSRF-Token header
- [ ] Test CSRF protection on state-changing endpoints

### Security Headers
- [ ] Verify Security Headers middleware is enabled
- [ ] Confirm HSTS header is active (production only)
- [ ] Review Content-Security-Policy for your use case
- [ ] Test security headers with securityheaders.com

### Input Validation
- [ ] Verify Input Validation middleware is enabled
- [ ] Review max request size limit (default: 10MB)
- [ ] Monitor SQL injection detection logs
- [ ] Test with various input patterns

### Error Tracking (Sentry)
- [ ] Set `SENTRY_DSN` if using Sentry (optional)
- [ ] Verify sensitive data filtering is working
- [ ] Configure alert rules in Sentry dashboard
- [ ] Set up notification channels (email, Slack, etc.)

## Environment Configuration

### Application Settings
- [ ] Set `APP_ENV=production`
- [ ] Set `DEBUG=False`
- [ ] Configure `API_HOST` and `API_PORT` appropriately
- [ ] Review and set appropriate `LOG_LEVEL` (INFO or WARNING recommended)

### External Services
- [ ] Configure `KNUSPR_API_KEY` if using Knuspr integration
- [ ] Verify external API endpoints are reachable
- [ ] Test API key authentication

### Redis Configuration
- [ ] Verify Redis is accessible at `REDIS_HOST:REDIS_PORT`
- [ ] Configure Redis password if needed
- [ ] Test Redis connection from application

## Monitoring & Observability

### Prometheus
- [ ] Verify Prometheus is scraping all targets
- [ ] Access http://localhost:9090/targets and confirm all UP
- [ ] Review and adjust scrape intervals if needed
- [ ] Configure retention period (default: 30 days)

### Grafana Dashboards
- [ ] Access Grafana at http://localhost:3000
- [ ] Verify all dashboards are loading:
  - API Overview
  - Database Monitoring
  - Business Metrics
- [ ] Configure datasources (Prometheus, Loki)
- [ ] Set up alert notification channels

### Loki & Promtail
- [ ] Verify Loki is receiving logs
- [ ] Test log queries in Grafana Explore
- [ ] Review log retention period (default: 30 days)
- [ ] Configure log aggregation labels

### Alerting
- [ ] Review alert rules in `/infrastructure/docker/prometheus/alerts.yml`
- [ ] Configure Alertmanager (if using)
- [ ] Set up notification channels (Slack, PagerDuty, email)
- [ ] Test alert firing and resolution

## Database

### Migrations
- [ ] Run all Alembic migrations: `alembic upgrade head`
- [ ] Verify database schema is up to date
- [ ] Backup database before migrations

### Backups
- [ ] Configure automated database backups
- [ ] Set `BACKUP_RETENTION` period (default: 30 days)
- [ ] Configure S3 backup upload (if using):
  - `S3_BUCKET`
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `AWS_DEFAULT_REGION`
- [ ] Test backup creation: `/usr/local/bin/backup_database.sh`
- [ ] Test backup restoration: `/usr/local/bin/restore_database.sh`
- [ ] Document backup and restore procedures

### Performance
- [ ] Review connection pool settings
- [ ] Monitor slow query logs
- [ ] Set up database indexes as needed
- [ ] Configure query timeouts

## Infrastructure

### Docker Compose
- [ ] Review resource limits for all services
- [ ] Verify all volumes are properly mounted
- [ ] Configure restart policies
- [ ] Review health check configurations

### Networking
- [ ] Restrict port access with firewall rules
- [ ] Use reverse proxy (nginx/traefik) for HTTPS
- [ ] Configure SSL/TLS certificates
- [ ] Enable HTTP to HTTPS redirect

### SSL/TLS
- [ ] Obtain SSL/TLS certificates (Let's Encrypt recommended)
- [ ] Configure reverse proxy with SSL
- [ ] Set up automatic certificate renewal
- [ ] Test SSL configuration with ssllabs.com

## Testing

### Functional Testing
- [ ] Run backend tests: `cd backend && pytest`
- [ ] Run frontend tests: `cd frontend && npm test`
- [ ] Run E2E tests: `cd frontend && npx playwright test`
- [ ] Verify all tests pass

### Security Testing
- [ ] Run security scan (OWASP ZAP, etc.)
- [ ] Test authentication flows
- [ ] Test authorization/permission checks
- [ ] Test rate limiting
- [ ] Test CSRF protection
- [ ] Review security headers

### Performance Testing
- [ ] Load test API endpoints
- [ ] Monitor response times under load
- [ ] Test database query performance
- [ ] Verify cache hit rates (Redis)

### Integration Testing
- [ ] Test frontend-backend integration
- [ ] Test Knuspr API integration (if enabled)
- [ ] Test email notifications (if enabled)
- [ ] Test webhook deliveries (if enabled)

## Deployment

### Pre-Deployment
- [ ] Review and merge all pending PRs
- [ ] Update CHANGELOG.md
- [ ] Tag release in git
- [ ] Backup production database
- [ ] Notify team of deployment window

### Deployment Steps
- [ ] Pull latest code: `git pull origin main`
- [ ] Install/update dependencies
  - Backend: `pip install -r requirements.txt`
  - Frontend: `npm install`
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Build Docker images: `docker-compose build`
- [ ] Start services: `docker-compose up -d`
- [ ] Verify all containers are running: `docker-compose ps`

### Post-Deployment
- [ ] Verify health checks: `curl http://localhost:8000/health`
- [ ] Check application logs: `docker-compose logs -f api`
- [ ] Monitor error rates in Grafana
- [ ] Verify Prometheus metrics
- [ ] Test critical user flows
- [ ] Monitor Sentry for errors (if enabled)

### Rollback Plan
- [ ] Document rollback procedure
- [ ] Keep previous Docker images available
- [ ] Keep database backup accessible
- [ ] Define rollback criteria (error rate threshold, etc.)

## Documentation

- [ ] Update API documentation
- [ ] Update README.md
- [ ] Document environment variables
- [ ] Document deployment procedures
- [ ] Document backup/restore procedures
- [ ] Document monitoring and alerting

## Team Readiness

- [ ] Train team on monitoring dashboards
- [ ] Document on-call procedures
- [ ] Set up PagerDuty/OpsGenie rotation (if applicable)
- [ ] Create runbooks for common issues
- [ ] Document escalation procedures

## Compliance & Legal

- [ ] Review data privacy requirements (GDPR, CCPA, etc.)
- [ ] Configure data retention policies
- [ ] Review terms of service
- [ ] Review privacy policy
- [ ] Document data processing agreements

## Final Verification

- [ ] All critical checklist items completed
- [ ] No wildcard CORS origins
- [ ] Strong passwords set for all services
- [ ] SSL/TLS enabled
- [ ] Monitoring and alerting configured
- [ ] Backups tested and verified
- [ ] Team notified and ready
- [ ] Rollback plan documented

---

## Quick Reference

### Critical Security Items
1. `CORS_ORIGINS` - NO wildcards!
2. `SECRET_KEY` - Strong, unique value
3. `JWT_SECRET_KEY` - Strong, unique value
4. `GRAFANA_ADMIN_PASSWORD` - Changed from default
5. `DB_PASSWORD` - Strong password
6. `APP_ENV=production` and `DEBUG=False`

### Service URLs (Default)
- API: http://localhost:8000
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Loki: http://localhost:3100

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/ready

# Prometheus targets
curl http://localhost:9090/api/v1/targets

# Loki ready
curl http://localhost:3100/ready
```

### Common Issues

**Issue**: CORS errors in browser
- **Solution**: Verify `CORS_ORIGINS` includes frontend domain

**Issue**: Grafana login fails
- **Solution**: Check `GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD`

**Issue**: Database connection failed
- **Solution**: Verify `DB_HOST`, `DB_PORT`, `DB_PASSWORD`

**Issue**: Prometheus not scraping
- **Solution**: Check target status at http://localhost:9090/targets

**Issue**: Sentry not capturing errors
- **Solution**: Verify `SENTRY_DSN` is set correctly
