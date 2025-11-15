# Recipe & Meal Planning API - Quick Start Guide

## Overview

This is a multi-agent recipe and meal planning system with a FastAPI backend, PostgreSQL database, Redis event bus, and monitoring stack.

## Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)

## Getting Started

### 1. Environment Setup

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` if you need to customize any settings.

### 2. Start with Docker Compose

Start all services (PostgreSQL, Redis, FastAPI, Prometheus, Grafana):

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL on port 5432
- Start Redis on port 6379
- Start FastAPI API on port 8000
- Start Prometheus on port 9090
- Start Grafana on port 3000
- Run database migrations automatically

### 3. Verify Installation

Check if the API is running:

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "recipe-meal-planning-api"
}
```

### 4. Explore the API Documentation

Open your browser to:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### 5. Run Migrations (if needed)

Migrations run automatically in Docker. For manual migration:

```bash
docker-compose exec api alembic upgrade head
```

## Local Development (without Docker)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start PostgreSQL and Redis

```bash
# Start PostgreSQL
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine
```

### 3. Run Migrations

```bash
alembic upgrade head
```

### 4. Start the API Server

```bash
python -m app.main
# or
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

### Recipe Endpoints

#### Harvest a Recipe
```bash
POST /api/v1/recipes/harvest
Content-Type: application/json
Authorization: Bearer <token>

{
  "url": "https://ottolenghi.co.uk/recipes/pasta-carbonara",
  "source_type": "html"
}
```

#### List Recipes
```bash
GET /api/v1/recipes?skip=0&limit=10
Authorization: Bearer <token>
```

#### Get Recipe by ID
```bash
GET /api/v1/recipes/{recipe_id}
Authorization: Bearer <token>
```

#### Update Recipe
```bash
PUT /api/v1/recipes/{recipe_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "Updated Recipe Title",
  "servings": 6
}
```

#### Delete Recipe
```bash
DELETE /api/v1/recipes/{recipe_id}
Authorization: Bearer <token>
```

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_recipe_harvester.py -v
pytest tests/test_api_recipes.py -v
```

## Monitoring

### Prometheus

Access Prometheus at http://localhost:9090

Available metrics:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration
- `recipe_harvest_total` - Total recipe harvests
- `recipe_harvest_failures_total` - Failed harvests

### Grafana

Access Grafana at http://localhost:3000

Default credentials:
- Username: `admin`
- Password: `admin`

## Architecture

```
┌─────────────────┐
│   FastAPI API   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│ DB   │  │ Redis │
│(PG)  │  │(Event)│
└──────┘  └───┬───┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼───────────┐  ┌────▼──────┐
│ Recipe        │  │ Ingredient│
│ Harvester     │  │ Intel     │
│ Agent         │  │ Agent     │
└───────────────┘  └───────────┘
```

## Troubleshooting

### Port Already in Use

If you see "port already in use" errors:

```bash
# Check what's using the port
lsof -i :8000

# Stop all containers
docker-compose down
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# View PostgreSQL logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d
```

### Redis Connection Issues

```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# View Redis logs
docker-compose logs redis
```

## Next Steps

1. **Authentication**: Implement JWT authentication endpoints (in progress)
2. **Ingredient Intelligence**: Add ingredient classification and substitution
3. **Meal Planning**: Implement meal planning with Z3 solver
4. **Knuspr Integration**: Add grocery cart synchronization

## Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests: `pytest`
4. Run linting: `black . && flake8`
5. Commit: `git commit -m "feat: your feature"`
6. Push: `git push origin feature/your-feature`

## Support

For issues or questions, check:
- API Documentation: http://localhost:8000/api/docs
- Project Plan: `specs/002-multi-agent-recipe-app/plan.md`
- Task List: `specs/002-multi-agent-recipe-app/tasks.md`
