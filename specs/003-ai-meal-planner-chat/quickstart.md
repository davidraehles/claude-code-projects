# Phase 1: Local Development Quickstart Guide

**Feature**: 003-ai-meal-planner-chat
**Date**: 2025-11-18
**Status**: Implementation Ready

---

## Overview

This guide walks you through setting up the AI Meal Planner Chat feature for local development. By the end, you'll have:

✅ Local backend running on `http://localhost:8000`
✅ Frontend running on `http://localhost:3000`
✅ PostgreSQL database with schema
✅ Redis cache
✅ Sample data for testing

**Time Estimate**: 20-30 minutes (first-time setup)

---

## Prerequisites

### System Requirements

- **OS**: Linux, macOS, or WSL2 (Windows)
- **Python**: 3.11+
- **Node.js**: 18+ (LTS)
- **Docker**: Latest (for PostgreSQL, Redis)
- **Git**: Latest

### Required API Keys

Before starting, obtain:

1. **Anthropic API Key** (Claude)
   - Sign up: https://console.anthropic.com
   - Create API key in Dashboard
   - Set env var: `ANTHROPIC_API_KEY`

2. **Deepgram API Key** (Speech-to-Text)
   - Sign up: https://console.deepgram.com
   - Create API key in Dashboard
   - Set env var: `DEEPGRAM_API_KEY` (optional for voice testing)

3. **Azure OpenAI API Key** (Text-to-Speech)
   - Sign up: https://azure.microsoft.com
   - Create resource: Cognitive Services > Text to Speech
   - Set env vars: `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` (optional)

### Verify Versions

```bash
# Python
python --version
# Expected: Python 3.11.x or 3.12.x

# Node.js
node --version
# Expected: v18.x.x or v20.x.x

# Docker
docker --version
# Expected: Docker version 24+

# Git
git --version
# Expected: git version 2.x+
```

---

## Step 1: Clone Repository

```bash
# Navigate to project directory (or clone if needed)
cd /home/darae/claude-code-projects

# Verify you're on the correct branch
git branch
# Expected: * 003-ai-meal-planner-chat

# Pull latest changes
git pull origin 003-ai-meal-planner-chat
```

---

## Step 2: Start Docker Services

### Start PostgreSQL and Redis

```bash
# From project root
docker-compose up -d postgres redis

# Verify services are running
docker ps
# Expected: Both postgres and redis containers should be running

# Test PostgreSQL connection
docker exec claude-code-postgres psql -U mealplanner_user -d meal_planner_db -c "SELECT 1"
# Expected: Output showing "1"

# Test Redis connection
docker exec claude-code-redis redis-cli ping
# Expected: PONG
```

---

## Step 3: Set Up Backend

### Install Python Dependencies

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -i fastapi
# Expected: fastapi version shown
```

### Configure Environment Variables

```bash
# Create .env file in backend/ directory
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://mealplanner_user:mealplanner_password@localhost:5432/meal_planner_db

# Redis
REDIS_URL=redis://localhost:6379/0

# API Keys
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
DEEPGRAM_API_KEY=YOUR_DEEPGRAM_KEY_HERE  # Optional
AZURE_SPEECH_KEY=YOUR_AZURE_KEY_HERE  # Optional
AZURE_SPEECH_REGION=eastus  # Or your region

# Environment
ENVIRONMENT=development
LOG_LEVEL=DEBUG
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# Feature Flags
ENABLE_VOICE_FEATURES=true
ENABLE_PROMPT_CACHING=true
EOF

# Replace YOUR_KEY_HERE with actual API keys
nano .env  # Edit with your keys
```

### Initialize Database

```bash
# Run migrations (assuming Alembic is configured)
alembic upgrade head

# Verify schema creation
docker exec claude-code-postgres psql -U mealplanner_user -d meal_planner_db -c "\dt"
# Expected: List of tables (users, chat_sessions, chat_messages, etc)

# Load sample data (optional)
python scripts/seed_test_data.py
# Expected: "Loaded X users, Y recipes, Z preferences"
```

### Start Backend Server

```bash
# In backend/ directory (virtual environment active)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

### Verify Backend is Running

```bash
# In a new terminal
curl http://localhost:8000/health
# Expected: {"status": "ok", "timestamp": "..."}

# Check API docs
open http://localhost:8000/docs
# Expected: Swagger UI loads with all endpoints documented
```

---

## Step 4: Set Up Frontend

### Install Node Dependencies

```bash
# Navigate to frontend directory
cd meal-planner-ui

# Install dependencies
npm install

# Verify installation
npm list next react
# Expected: Versions shown (Next.js 14+, React 18+)
```

### Configure Environment Variables

```bash
# Create .env.local in meal-planner-ui/ directory
cat > .env.local << 'EOF'
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Feature Flags
NEXT_PUBLIC_ENABLE_VOICE=true
NEXT_PUBLIC_ENABLE_ANALYTICS=false  # Disable in dev

# Environment
NODE_ENV=development
EOF
```

### Start Frontend Server

```bash
# In meal-planner-ui/ directory
npm run dev

# Expected output:
# ▲ Next.js 14.x.x
# - Local:        http://localhost:3000
```

### Verify Frontend is Running

```bash
# Open in browser
open http://localhost:3000

# Expected: Meal planner home page loads (or login page if auth required)
```

---

## Step 5: Test the Integration

### API Contract Testing

```bash
# Test Chat API
curl -X POST http://localhost:8000/v1/chat/sessions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"voice_enabled": false}'

# Expected Response:
# {
#   "session_id": "uuid",
#   "created_at": "2025-11-18T...",
#   "initial_message": {...},
#   "websocket_url": "wss://..."
# }
```

### End-to-End Chat Flow

```bash
# 1. Create a chat session
SESSION_ID=$(curl -X POST http://localhost:8000/v1/chat/sessions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | jq -r '.session_id')

# 2. Send a message
curl -X POST "http://localhost:8000/v1/chat/sessions/$SESSION_ID/messages" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "I want to create a meal plan. I am vegetarian and allergic to peanuts."}'

# Expected: Message is created and queued for LLM processing

# 3. Get conversation history
curl -X GET "http://localhost:8000/v1/chat/sessions/$SESSION_ID/messages" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected: Array of messages including your message and AI response
```

### Test Preferences API

```bash
# Save user preferences
curl -X POST http://localhost:8000/v1/preferences \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dietary_restrictions": ["vegetarian"],
    "allergies": [{"allergen": "peanut", "severity": "severe"}],
    "cuisine_preferences": ["mediterranean", "asian"],
    "cooking_skill": "intermediate",
    "household_size": 2,
    "max_prep_time_minutes": 45
  }'

# Expected: 201 Created with preferences ID and values

# Retrieve preferences
curl -X GET http://localhost:8000/v1/preferences \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Expected: Same preferences returned
```

### Test Meal Plan API

```bash
# Generate a meal plan
curl -X POST http://localhost:8000/v1/meal-plans \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"duration_days\": 7}"

# Expected: 201 Created with meal plan containing 7 days of meals

# Verify allergen compliance
# (All meals should NOT contain peanuts)
```

---

## Step 6: Run Tests

### Backend Tests

```bash
# In backend/ directory
pytest tests/unit/test_chat_service.py -v
pytest tests/integration/test_chat_flow.py -v
pytest tests/contract/test_chat_api.py -v

# Expected: All tests pass (✓)
```

### Frontend Tests

```bash
# In meal-planner-ui/ directory
npm run test

# Expected: Jest runs and shows test summary
```

### E2E Tests

```bash
# In meal-planner-ui/ directory
npm run test:e2e

# Expected: Playwright launches browser and runs tests
```

---

## Common Development Workflows

### Add a New Endpoint

```bash
# 1. Update OpenAPI contract (contracts/chat-api.openapi.yaml)
# 2. Create endpoint in backend/app/api/v1/chat.py
# 3. Add service logic in backend/app/services/chat_service.py
# 4. Write tests: backend/tests/contract/test_chat_api.py
# 5. Test with curl (see Step 5)
```

### Debug LLM Calls

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Restart backend
# uvicorn logs will now show:
# - Full prompt sent to Claude
# - Full response from Claude
# - Token usage
# - Cost estimate
```

### Work with WebSocket (Real-Time Chat)

```bash
# Backend automatically upgrades HTTP to WebSocket
# Use tool like websocat to test:

websocat ws://localhost:8000/ws/chat/sessions/YOUR_SESSION_ID

# Send message:
{"type": "message", "content": "Hello!"}

# Expected response:
{"type": "message:new", "message": {...}}
```

### Clear Test Data

```bash
# Drop all tables and recreate schema
docker exec claude-code-postgres psql -U mealplanner_user -d meal_planner_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Reload schema
alembic upgrade head

# Reload sample data
python scripts/seed_test_data.py
```

---

## Troubleshooting

### PostgreSQL Connection Failed

```bash
# Check if container is running
docker ps | grep postgres

# Check logs
docker logs claude-code-postgres

# Verify credentials in .env
cat .env | grep DATABASE_URL

# Test connection directly
docker exec -it claude-code-postgres psql -U mealplanner_user -W
# (Enter password: mealplanner_password)
```

### Redis Connection Failed

```bash
# Check if container is running
docker ps | grep redis

# Test connection
redis-cli -h localhost ping
# Expected: PONG

# Check REDIS_URL in .env
cat .env | grep REDIS_URL
```

### LLM API Errors

```bash
# Verify API key is set
echo $ANTHROPIC_API_KEY
# Expected: sk-ant-...

# Check if key is valid
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model": "claude-3-5-haiku-20241022", "max_tokens": 10, "messages": [{"role": "user", "content": "test"}]}'

# Expected: Response from Claude API (not 401)
```

### Frontend Can't Connect to Backend

```bash
# Verify backend is running
curl http://localhost:8000/health
# Expected: {"status": "ok"}

# Check NEXT_PUBLIC_API_URL in .env.local
cat meal-planner-ui/.env.local | grep API_URL

# Check browser console (F12) for CORS errors
# Backend might need CORS configuration
```

### WebSocket Connection Issues

```bash
# Check if WebSocket endpoint exists
curl -v http://localhost:8000/ws/chat/sessions/test-id \
  -H "Upgrade: websocket" \
  -H "Connection: Upgrade"

# Expected: 101 Switching Protocols (successful WebSocket upgrade)
```

---

## Next Steps After Setup

### 1. Create Your First Chat Session

1. Navigate to `http://localhost:3000`
2. Log in (or create test account)
3. Click "Start Chat"
4. Ask: "I'm vegetarian and allergic to peanuts. I want a meal plan for next week."
5. Observe AI response and meal plan generation

### 2. Explore API Documentation

- Backend API Docs: http://localhost:8000/docs
- OpenAPI Schemas: `specs/003-ai-meal-planner-chat/contracts/`
- Interactive testing: Use Swagger UI or Postman

### 3. Review Code Structure

```
backend/
├── app/api/v1/
│   ├── chat.py          # Chat endpoints
│   ├── preferences.py   # Preference endpoints
│   ├── voice.py         # Voice endpoints
│   └── meal_plans.py    # Meal plan endpoints
├── app/services/
│   ├── chat_service.py       # LLM orchestration
│   ├── preference_service.py # Preference logic
│   ├── voice_service.py      # Voice processing
│   └── meal_plan_service.py  # Meal plan generation
└── tests/
    ├── unit/
    ├── integration/
    └── contract/

frontend/
├── src/components/
│   ├── chat/
│   │   ├── ChatInterface.tsx
│   │   ├── ChatMessage.tsx
│   │   └── VoiceInput.tsx
│   ├── preferences/
│   │   └── PreferenceManager.tsx
│   └── meal-plan/
│       └── MealPlanDisplay.tsx
└── tests/
    ├── e2e/
    └── unit/
```

### 4. Start Implementation (Phase 2)

When ready to implement:

```bash
# Generate implementation tasks
/speckit.tasks

# Follow the generated tasks.md step-by-step
cat specs/003-ai-meal-planner-chat/tasks.md
```

---

## Development Best Practices

### Commit Frequently

```bash
git add .
git commit -m "feat: Add chat message intent detection"
```

### Run Tests Before Committing

```bash
pytest tests/ -v
npm run test --prefix meal-planner-ui
```

### Monitor API Costs

```bash
# Check token usage in logs
grep "tokens_used" backend/logs/*.log

# Estimate monthly cost
# = total_tokens / 1_000_000 * RATE_PER_MILLION
# Claude Haiku: $1 per 1M input, $5 per 1M output
```

### Check Database Indexes

```bash
# Monitor slow queries
docker exec claude-code-postgres psql -U mealplanner_user -d meal_planner_db \
  -c "SELECT query, calls, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10"
```

---

## Docker Cleanup

### Stop Services

```bash
docker-compose down
```

### Remove Data (Reset Database)

```bash
docker-compose down -v  # -v removes volumes (DELETES DATA!)
```

### View Logs

```bash
# PostgreSQL
docker logs claude-code-postgres -f

# Redis
docker logs claude-code-redis -f

# Both
docker-compose logs -f
```

---

## Resources

- **Architecture**: See `specs/003-ai-meal-planner-chat/data-model.md`
- **API Contracts**: See `specs/003-ai-meal-planner-chat/contracts/`
- **Implementation Plan**: See `specs/003-ai-meal-planner-chat/plan.md`
- **Research & Decisions**: See `specs/003-ai-meal-planner-chat/research.md`
- **Feature Spec**: See `specs/003-ai-meal-planner-chat/spec.md`

---

## Support & Questions

For issues or questions:

1. Check this troubleshooting section
2. Review API docs (http://localhost:8000/docs)
3. Check backend logs: `docker logs claude-code-postgres`
4. Open issue in repository

---

## Status Checklist

Use this checklist to verify everything is working:

- [ ] PostgreSQL container running (`docker ps | grep postgres`)
- [ ] Redis container running (`docker ps | grep redis`)
- [ ] Backend running on http://localhost:8000
- [ ] Backend health check passes (`curl http://localhost:8000/health`)
- [ ] Frontend running on http://localhost:3000
- [ ] Can create chat session (`curl -X POST http://localhost:8000/v1/chat/sessions`)
- [ ] Can send message (`curl -X POST http://localhost:8000/v1/chat/sessions/.../messages`)
- [ ] Can save preferences (`curl -X POST http://localhost:8000/v1/preferences`)
- [ ] Can generate meal plan (`curl -X POST http://localhost:8000/v1/meal-plans`)
- [ ] Backend tests pass (`pytest tests/ -v`)
- [ ] Frontend tests pass (`npm run test --prefix meal-planner-ui`)

✅ **All checks passing? You're ready to start development!**
