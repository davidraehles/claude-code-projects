# Railway Migration Strategy

## Overview
This deployment uses Railway's `startCommand` to run database migrations during the deployment phase, separate from normal app restarts.

## How It Works

### Deployment Flow
1. Railway builds the Docker image
2. Railway starts the container with `startCommand`
3. `startCommand` runs: `alembic upgrade head && uvicorn app.main:app ...`
4. Migrations execute first (one-time during deployment)
5. App starts only if migrations succeed

### Key Benefits
- ✅ Migrations run once per deployment, not on every restart
- ✅ App won't start if migrations fail (safe deployment)
- ✅ Separate concerns: deployment vs runtime
- ✅ Works with Railway's deployment lifecycle
- ✅ No custom scripts needed

### Configuration
In `railway.toml`:
```toml
[deploy]
startCommand = "sh -c 'alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}'"
```

## When Migrations Run
- ✅ On new deployments (git push)
- ✅ On manual redeployments
- ❌ NOT on container restarts (failures, scale events)
- ❌ NOT on health check failures

## Manual Migration
If needed, you can still run migrations manually:
```bash
railway run alembic upgrade head
```

## Rollback
To rollback the last migration:
```bash
railway run alembic downgrade -1
```

## Monitoring
Check Railway logs during deployment to see migration execution:
```
Running database migrations...
✅ Migrations completed successfully
Starting application...
```

## Best Practices
1. Test migrations locally first
2. Keep migrations fast (<30s)
3. Use Railway's rollback feature if needed
4. Monitor deployment logs for errors

## Documentation
For more details, see: [docs/RAILWAY_MIGRATION_STRATEGY.md](../docs/RAILWAY_MIGRATION_STRATEGY.md)
