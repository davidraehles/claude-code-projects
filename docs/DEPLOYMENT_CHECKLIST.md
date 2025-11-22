# 🚀 Production Deployment Checklist

**Application**: MealPlannerAI
**Version**: 1.0
**Deployment Date**: _________________
**Deployed By**: _________________

---

## Pre-Deployment (1 Week Before)

### Code Freeze & Testing
- [ ] All features complete and merged to main
- [ ] All tests passing (unit, integration, E2E)
- [ ] Code review completed
- [ ] No critical security issues identified
- [ ] Performance benchmarks acceptable
- [ ] Database migrations tested locally
- [ ] Error scenarios tested

### Documentation
- [ ] README updated with production instructions
- [ ] API documentation up-to-date
- [ ] Architecture diagrams reviewed
- [ ] Runbook created for on-call engineers
- [ ] Disaster recovery procedures documented
- [ ] Database backup/restore procedures tested

### Infrastructure Preparation
- [ ] Railway account created and configured
- [ ] Vercel account created and configured
- [ ] GitHub OAuth tokens generated (if needed)
- [ ] Monitoring tools set up (Sentry, DataDog, etc.)
- [ ] Log aggregation configured (if applicable)
- [ ] Backup strategy documented

---

## Security & Secrets (Day Before)

### Secret Generation
- [ ] Run `scripts/generate_production_secrets.sh`
- [ ] Generate 6 new secrets:
  - [ ] `SECRET_KEY`
  - [ ] `JWT_SECRET_KEY`
  - [ ] `KNUSPR_ENCRYPTION_KEY`
  - [ ] `NEXTAUTH_SECRET`
  - [ ] `DB_PASSWORD` (if custom)
  - [ ] `REDIS_PASSWORD` (if custom)
- [ ] Store securely (password manager, encrypted file)
- [ ] Share with team leads only (encrypted channel)
- [ ] Verify no secrets committed to Git

### Security Review
- [ ] HTTPS enabled for all endpoints
- [ ] CORS properly configured (not wildcard in production)
- [ ] JWT expiration set appropriately (1 hour recommended)
- [ ] CSRF protection enabled
- [ ] SQL injection prevention verified
- [ ] XSS protection enabled
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints

### Encryption
- [ ] Database encryption enabled (Railway PostgreSQL)
- [ ] Credential encryption verified (Fernet keys generated)
- [ ] TLS certificates valid
- [ ] API calls use HTTPS only

---

## Infrastructure Setup (Day Before)

### Railway Backend Configuration
- [ ] Create Railway project
- [ ] Add PostgreSQL service
- [ ] Add Redis service
- [ ] Connect GitHub repository
- [ ] Configure environment variables:
  - [ ] `DB_*` (from PostgreSQL service)
  - [ ] `REDIS_*` (from Redis service)
  - [ ] `SECRET_KEY`
  - [ ] `JWT_SECRET_KEY`
  - [ ] `KNUSPR_ENCRYPTION_KEY`
  - [ ] `APP_ENV=production`
  - [ ] `DEBUG=False`
  - [ ] `CORS_ORIGINS=<vercel-url>`
- [ ] Configure health check: `/health` (already set in railway.toml)
- [ ] Set restart policy: ON_FAILURE with max 10 retries
- [ ] Configure domain (custom or use Railway default)

### Vercel Frontend Configuration
- [ ] Create Vercel project
- [ ] Connect GitHub repository
- [ ] Configure environment variables:
  - [ ] `NEXT_PUBLIC_API_URL=<railway-url>`
  - [ ] `NEXTAUTH_SECRET`
  - [ ] `NEXTAUTH_URL=<vercel-url>`
- [ ] Configure build settings (auto-detected)
- [ ] Set production branch: `main`
- [ ] Configure custom domain (optional)

### Database Preparation
- [ ] PostgreSQL created on Railway
- [ ] Redis created on Railway
- [ ] Database credentials verified
- [ ] Backup strategy enabled
- [ ] Connection pooling configured (if applicable)

---

## Pre-Launch Testing (Day Of)

### Backend Health Check
- [ ] Health endpoint responds: `GET /health` → 200
- [ ] PostgreSQL connected: logs show "Database connected"
- [ ] Redis connected: logs show "Redis connected"
- [ ] All services responding within SLA (<500ms)

### API Testing
- [ ] User registration works
- [ ] User login works
- [ ] JWT token issued and validated
- [ ] Protected endpoints require auth token
- [ ] Error responses are user-friendly
- [ ] Rate limiting active

### Frontend Testing
- [ ] Vercel build succeeds
- [ ] Landing page loads
- [ ] Login/signup flows work
- [ ] Redirect after auth works
- [ ] Dashboard loads and displays recipes
- [ ] Can create new recipe
- [ ] Can generate meal plan
- [ ] Can view meal plan details
- [ ] Knuspr setup button visible
- [ ] Knuspr cart generation works (if credentials configured)

### End-to-End Flow
- [ ] Register new user
- [ ] Import sample recipes
- [ ] Generate meal plan
- [ ] View meal plan
- [ ] See Knuspr cart option
- [ ] (Optional) Configure Knuspr and generate cart
- [ ] Logout and re-login

### Performance Testing
- [ ] Homepage loads in <2s
- [ ] API response times <500ms
- [ ] Meal plan generation completes in <30s
- [ ] No N+1 queries in logs
- [ ] Memory usage stable (not increasing)

---

## Go-Live (Launch Hour)

### Final Checks (15 minutes before)
- [ ] All team members online and ready
- [ ] Communication channel open (Slack, Discord)
- [ ] Monitoring dashboards accessible
- [ ] Database backups completed
- [ ] Runbook printed/available
- [ ] Escalation contacts available

### Deployment Execution
- [ ] Enable auto-deploy on Railway (if not already)
- [ ] Trigger Vercel deployment
- [ ] Monitor deployment logs
- [ ] Wait for health checks to pass
- [ ] Verify application is running
- [ ] Announce go-live in team channel

### Smoke Testing (Post-Launch)
- [ ] Visit production URL in browser
- [ ] Complete registration flow
- [ ] Complete login flow
- [ ] Use primary features
- [ ] Check for error messages
- [ ] Monitor error rate (<1%)

### Monitoring & Alerts
- [ ] Error tracking enabled (Sentry, etc.)
- [ ] Log aggregation streaming
- [ ] Performance metrics being recorded
- [ ] Uptime monitors active
- [ ] Alert notifications configured
- [ ] On-call escalation path active

---

## Post-Launch (First 24 Hours)

### Continuous Monitoring
- [ ] Monitor error rates (target: <1%)
- [ ] Check API response times (target: <500ms)
- [ ] Verify database health
- [ ] Check Redis cache hit rates
- [ ] Monitor user registrations/signups
- [ ] Watch for unusual traffic patterns

### User Feedback
- [ ] Monitor user reports/feedback
- [ ] Track support tickets
- [ ] Note any usability issues
- [ ] Document unexpected behaviors

### Incident Response
- [ ] If errors spike:
  - [ ] Check logs for root cause
  - [ ] Roll back if necessary (git revert)
  - [ ] Deploy fix
  - [ ] Notify users
  - [ ] Post-mortem after 24h
- [ ] If performance degrades:
  - [ ] Check query performance
  - [ ] Verify database indexes
  - [ ] Check for memory leaks
  - [ ] Scale services if needed

### Team Debrief
- [ ] Schedule post-launch review
- [ ] Identify what went well
- [ ] Identify what could improve
- [ ] Document lessons learned
- [ ] Update runbooks based on findings

---

## Post-Launch (First Week)

### Stability Verification
- [ ] No critical bugs reported
- [ ] Error rate stable (<1%)
- [ ] Performance metrics stable
- [ ] Database size growing normally
- [ ] No unusual resource usage

### Feature Verification
- [ ] All features working as expected
- [ ] No regressions from previous version
- [ ] User flow working smoothly
- [ ] Knuspr integration working (if enabled)

### Monitoring Setup
- [ ] Daily log review for 7 days
- [ ] Weekly metrics review
- [ ] Monthly performance benchmarks
- [ ] Quarterly security audit scheduled

### Communication
- [ ] Announce launch in public channels
- [ ] Create user documentation
- [ ] Prepare FAQ based on early feedback
- [ ] Set up user communication channels

---

## Post-Launch (First Month)

### Optimization
- [ ] Optimize slow queries based on metrics
- [ ] Improve error messages based on user feedback
- [ ] Refactor problematic code identified in monitoring
- [ ] Optimize database schema if needed

### Documentation
- [ ] Update README with real deployment info
- [ ] Document actual deployment times
- [ ] Document actual resource usage
- [ ] Update API documentation with real examples

### Team Training
- [ ] Train support team on known issues
- [ ] Create troubleshooting guides
- [ ] Update runbooks with real scenarios
- [ ] Document escalation procedures

### Planning
- [ ] Schedule next release cycle
- [ ] Plan infrastructure improvements
- [ ] Plan feature enhancements
- [ ] Set SLA targets

---

## Rollback Procedure (If Needed)

### Quick Rollback
```bash
# If critical issue occurs, rollback to previous version

# On Railway
railway shell
git reset --hard <previous-commit>
git push --force

# On Vercel
# Go to Vercel dashboard → Deployments → Select previous → Promote to Production
```

### Rollback Criteria
- [ ] Unrecoverable database state
- [ ] Complete service unavailability (>10 min)
- [ ] Security breach detected
- [ ] Major data loss or corruption
- [ ] Cannot identify/fix cause within 30 minutes

### Post-Rollback Actions
1. [ ] Notify all users (status page, email)
2. [ ] Document what happened
3. [ ] Identify root cause
4. [ ] Fix and test thoroughly
5. [ ] Schedule re-deployment for next day
6. [ ] Conduct incident post-mortem
7. [ ] Improve deployment/testing process

---

## Sign-Off

**Deployment Manager**: _____________________ Date: _______

**Backend Lead**: _____________________ Date: _______

**Frontend Lead**: _____________________ Date: _______

**DevOps Lead**: _____________________ Date: _______

---

## Notes & Issues Found

```
[Add any issues, solutions, or notes discovered during deployment]




```

---

## Related Documents

- [PRODUCTION_SETUP.md](./PRODUCTION_SETUP.md) - Detailed setup guide
- [CRITICAL_PATH_TO_PRODUCTION.md](./CRITICAL_PATH_TO_PRODUCTION.md) - Project status
- [README.md](../README.md) - Project overview
