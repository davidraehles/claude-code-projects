# Railway Multi-Service Configuration

This directory contains the Railway multi-service configuration for PR environments and production deployments.

## Overview

The `services.json` file defines a complete application stack:

1. **Backend** - FastAPI application with automatic database migrations
2. **PostgreSQL** - Database with persistent storage
3. **Redis** - Cache/session store with persistent storage

## Service Details

### Backend Service
- **Source**: GitHub repository (root directory)
- **Build**: Uses `backend/Dockerfile`
- **Start**: Runs migrations (`alembic upgrade head`) then starts app
- **Health Check**: `/health` endpoint with 100s timeout
- **Restart Policy**: On failure, max 3 retries
- **Public Domain**: Enabled for external access

### PostgreSQL Service
- **Image**: `postgres:15-alpine`
- **Storage**: Persistent volume at `/var/lib/postgresql/data`
- **Environment Variables**:
  - `POSTGRES_DB` (defaults to `recipe_app`)
  - `POSTGRES_USER` (defaults to `postgres`)
  - `POSTGRES_PASSWORD` (required - set in Railway dashboard)
- **Health Check**: `pg_isready` every 10s

### Redis Service
- **Image**: `redis:7-alpine`
- **Storage**: Persistent volume at `/data` with AOF enabled
- **Configuration**: Append-only file with `everysec` fsync
- **Health Check**: `redis-cli ping` every 10s

## PR Environment Configuration

The `pr` environment is configured for automatic PR deployments:

- **autoLink**: `true` - Automatically links services in PR environments
- **autoClone**: `true` - Clones production services for each PR
- **autoRemove**: `true` - Removes environment when PR is closed/merged

## Environment Variables

The backend service automatically receives these variables from linked services:

- `DATABASE_URL` - PostgreSQL connection string (auto-generated)
- `REDIS_URL` - Redis connection string (auto-generated)

Additional variables needed:
- `JWT_SECRET_KEY` - JWT signing secret
- `NEXTAUTH_SECRET` - NextAuth.js secret
- `KNUSPR_EMAIL` - Knuspr integration email (optional)
- `KNUSPR_PASSWORD` - Knuspr integration password (optional)

## Deployment Flow

### PR Environment
1. PR opened → Railway creates new environment
2. Services are cloned from production
3. Backend builds and deploys
4. Migrations run automatically on startup
5. Health checks verify all services are ready
6. PR environment URL is generated

### Production
1. Push to main branch → Railway detects changes
2. Backend rebuilds and deploys
3. Migrations run (idempotent - safe to rerun)
4. Zero-downtime deployment with health checks
5. Production URL remains stable

## Volume Persistence

Volumes are persistent and survive deployments:

- **postgres_data**: Database files (critical data)
- **redis_data**: Redis AOF file (cache/sessions)

## Health Checks

All services have health checks configured:

| Service | Command | Interval | Timeout | Retries |
|---------|---------|----------|---------|---------|
| Backend | GET /health | N/A | 100s | N/A |
| PostgreSQL | pg_isready | 10s | 5s | 5 |
| Redis | redis-cli ping | 10s | 3s | 5 |

## Troubleshooting

### Backend won't start
1. Check Railway logs for migration errors
2. Verify DATABASE_URL is set and accessible
3. Check healthcheck timeout (may need increase for large migrations)

### Database connection errors
1. Verify PostgreSQL service is running
2. Check DATABASE_URL format: `postgresql://user:pass@host:port/db`
3. Ensure backend and postgres are in same environment

### Redis connection issues
1. Redis is optional - app will run with degraded status
2. Check REDIS_URL format: `redis://host:port`
3. Verify redis service is healthy

## Best Practices

1. **Always test migrations in PR environments first**
2. **Monitor health check timeouts** - adjust if migrations are slow
3. **Keep DATABASE_URL and REDIS_URL as auto-generated** - don't override
4. **Set POSTGRES_PASSWORD securely** via Railway dashboard
5. **Use Railway's built-in secrets** for sensitive variables

## Links

- [Railway Documentation](https://docs.railway.app/)
- [Railway Multi-Service Apps](https://docs.railway.app/guides/multi-service-apps)
- [Railway PR Environments](https://docs.railway.app/guides/environments#pr-environments)
