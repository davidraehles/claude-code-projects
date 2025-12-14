#!/bin/bash
# Quick reference commands for Phase 1 deployed system

echo "🚀 Knuspr Integration - Phase 1 Quick Reference"
echo "=============================================="
echo ""

# Docker Commands
echo "📦 Docker Services:"
echo "  Status:          docker compose ps"
echo "  Start:           docker compose up -d"
echo "  Stop:            docker compose down"
echo "  Rebuild:         docker compose build --no-cache"
echo "  Logs (all):      docker compose logs -f"
echo "  Logs (API):      docker logs -f recipe-api"
echo ""

# Database Commands
echo "🗄️  Database:"
echo "  Connect:         docker exec -it recipe-postgres psql -U postgres -d recipe_app"
echo "  Check tables:    docker exec recipe-postgres psql -U postgres -d recipe_app -c '\dt'"
echo "  Migration status: cd backend && python3 -m alembic current"
echo "  Run migrations:  cd backend && python3 -m alembic upgrade head"
echo ""

# API Testing
echo "🧪 API Testing:"
echo "  Health check:    curl http://localhost:8000/health"
echo "  API docs:        open http://localhost:8000/docs"
echo "  Metrics:         curl http://localhost:8000/metrics"
echo ""

# Phase 1 Endpoints
echo "✨ Phase 1 Endpoints:"
echo "  Auth status:     GET  /api/v1/knuspr-credentials/auth/status"
echo "  Update cart:     PUT  /api/v1/grocery-carts/{id}"
echo "  Checkout:        POST /api/v1/grocery-carts/{id}/checkout"
echo ""

# Validation
echo "✅ Validation:"
echo "  Run tests:       ./validate-phase1.sh"
echo "  Check headers:   curl -sI http://localhost:8000/health | grep -i x-"
echo "  Check rate limits: curl -sI http://localhost:8000/health | grep -i rate"
echo ""

# Monitoring
echo "📊 Monitoring:"
echo "  Prometheus:      open http://localhost:9090"
echo "  Grafana:         open http://localhost:3000"
echo ""

# Useful Aliases
echo "💡 Tip: Add these aliases to your ~/.bashrc:"
echo "  alias dc='docker compose'"
echo "  alias dps='docker compose ps'"
echo "  alias dlogs='docker compose logs -f'"
echo "  alias dapi='docker logs -f recipe-api'"
echo ""
