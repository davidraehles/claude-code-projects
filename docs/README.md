# AI Meal Planner - Documentation

Comprehensive documentation for the AI Meal Planner application with multi-agent architecture.

**Last Updated**: November 29, 2025

---

## Quick Navigation

### New to the Project?
1. [QUICKSTART.md](QUICKSTART.md) - Local development setup (15 min)
2. [DEPLOYMENT.md](DEPLOYMENT.md) - Deploy to Railway + Vercel (30 min)
3. [../README.md](../README.md) - Project overview and tech stack

### For Developers
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Running tests (unit, integration, E2E)
- [VSCODE_DEVELOPMENT_READY.md](VSCODE_DEVELOPMENT_READY.md) - VSCode configuration
- [CLI_TOOLS.md](CLI_TOOLS.md) - Railway & Vercel CLI reference
- [../CLAUDE.md](../CLAUDE.md) - AI development guidelines

### Architecture & Design
- [../.claude/agents/README.md](../.claude/agents/README.md) - Multi-agent system overview
- [../.claude/agents/AGENT-REGISTRY.md](../.claude/agents/AGENT-REGISTRY.md) - All 8 agents
- [ARCHITECTURE_DEBT.md](ARCHITECTURE_DEBT.md) - Technical debt tracking

---

## Documentation by Category

### Getting Started

| Document | Purpose | Time |
|----------|---------|------|
| [QUICKSTART.md](QUICKSTART.md) | Local development with Docker | 15 min |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment guide | 30 min |
| [CLI_TOOLS.md](CLI_TOOLS.md) | Railway/Vercel CLI commands | Reference |

### Development

| Document | Purpose |
|----------|---------|
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Manual testing procedures |
| [VSCODE_DEVELOPMENT_READY.md](VSCODE_DEVELOPMENT_READY.md) | VSCode setup & extensions |
| [GROCERY_WORKFLOW.md](GROCERY_WORKFLOW.md) | Grocery list generation workflow |
| [KNUSPR_SETUP_GUIDE.md](KNUSPR_SETUP_GUIDE.md) | Knuspr MCP integration |

### Architecture & Planning

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE_DEBT.md](ARCHITECTURE_DEBT.md) | Technical debt & refactoring plans |
| [WEB_APP_MVP_PLAN.md](WEB_APP_MVP_PLAN.md) | MVP implementation roadmap |
| [SPECKIT_MIGRATION_PLAN.md](SPECKIT_MIGRATION_PLAN.md) | Spec-Kit migration strategy |

### Project Status & History

| Document | Purpose |
|----------|---------|
| [PHASE_1_COMPLETE.md](PHASE_1_COMPLETE.md) | Phase 1 milestones |
| [PHASE_2_STATUS.md](PHASE_2_STATUS.md) | Phase 2 progress |
| [PHASE_3_TESTING_GUIDE.md](PHASE_3_TESTING_GUIDE.md) | Phase 3 testing |
| [PHASE_4_FRONTEND_STATUS.md](PHASE_4_FRONTEND_STATUS.md) | Phase 4 frontend work |
| [PHASE_5_TESTING_SUMMARY.md](PHASE_5_TESTING_SUMMARY.md) | Phase 5 E2E testing |

### Deployment & Operations

| Document | Purpose |
|----------|---------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Full deployment guide |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Pre-deployment checklist |
| [DEPLOYMENT_READINESS_PLAN.md](DEPLOYMENT_READINESS_PLAN.md) | Production readiness |
| [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md) | Production configuration |
| [CRITICAL_PATH_TO_PRODUCTION.md](CRITICAL_PATH_TO_PRODUCTION.md) | Critical production tasks |

### Debugging & Fixes

| Document | Purpose |
|----------|---------|
| [AUTH_DEBUG_REPORT.md](AUTH_DEBUG_REPORT.md) | Authentication debugging |
| [AUTH_FIX_RESOLUTION.md](AUTH_FIX_RESOLUTION.md) | Auth fix summary |
| [JWT_EXCEPTION_FIX.md](JWT_EXCEPTION_FIX.md) | JWT token handling |
| [TOKEN_EXPIRY_FIX.md](TOKEN_EXPIRY_FIX.md) | Token expiry issues |
| [MEAL_PLAN_DEBUG_GUIDE.md](MEAL_PLAN_DEBUG_GUIDE.md) | Meal plan debugging |
| [DEPLOYMENT_FIX.md](DEPLOYMENT_FIX.md) | Deployment fixes |

### Testing Reports

| Document | Purpose |
|----------|---------|
| [PLAYWRIGHT_TEST_REPORT.md](PLAYWRIGHT_TEST_REPORT.md) | E2E test results |
| [TEST_EXECUTION_SUMMARY.md](TEST_EXECUTION_SUMMARY.md) | Test execution summary |
| [MEAL_PLAN_TESTS_FIXED.md](MEAL_PLAN_TESTS_FIXED.md) | Meal plan test fixes |

---

## Multi-Agent System Documentation

This project uses 8 specialized ReAct agents for parallelized development:

1. **Router Agent** - Task orchestration and parallelization
2. **Spec Analyzer Agent** - Deep requirement analysis
3. **Frontend Dev Agent** - React/Next.js/TypeScript implementation
4. **Backend Dev Agent** - Python/FastAPI/SQLAlchemy implementation
5. **Testing & Quality Agent** - Comprehensive test generation
6. **Documentation Agent** - Spec/code synchronization
7. **Integration Agent** - Final validation and merge readiness
8. **Agent Registry Manager** - Agent lifecycle management

**Full Documentation**: [../.claude/agents/README.md](../.claude/agents/README.md)

---

## Feature Specifications

All feature specs are located in `/specs/` and use the Spec-Kit framework:

- [Feature 001 - Grocery List Generation](../specs/001-grocery-list-generation/spec.md)
- [Feature 002 - Multi-Agent Recipe App](../specs/002-multi-agent-recipe-app/spec.md)
- [Feature 003 - AI Meal Planner Chat](../specs/003-ai-meal-planner-chat/spec.md)

---

## Live Deployments

- **Frontend**: https://claude-code-projects.vercel.app
- **Backend API**: https://claude-code-projects-production.up.railway.app
- **API Docs**: https://claude-code-projects-production.up.railway.app/api/docs

---

## Troubleshooting Archive

Historical troubleshooting documentation is archived in:
- [archive/](archive/) - Railway, Vercel, bcrypt, NextAuth fixes

---

## Key Learnings

### 1. Bcrypt Password Hashing
**Problem**: passlib's `bcrypt.hash()` requires explicit configuration

**Solution**:
```python
return bcrypt.using(ident="2b", rounds=12).hash(password)
```

### 2. Vercel NextAuth Proxy
**Problem**: Proxying `/api/*` breaks NextAuth routes

**Solution**: Only proxy backend routes:
```json
{"source": "/api/v1/:path*"}
```

### 3. Railway Environment Variables
**Problem**: Typing `${{Service.VAR}}` as text doesn't work

**Solution**: Use Railway's **Reference** feature

---

## Need Help?

- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment troubleshooting
- Check [TESTING_GUIDE.md](TESTING_GUIDE.md) for testing issues
- Check [CLI_TOOLS.md](CLI_TOOLS.md) for CLI command reference
- Check [archive/](archive/) for historical fixes
