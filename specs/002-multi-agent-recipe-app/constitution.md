# Multi-Agent Recipe and Meal Planning System Constitution

**Feature Branch**: `002-multi-agent-recipe-app`
**Version**: 1.0.0 | **Ratified**: 2025-11-14 | **Type**: Multi-tenant SaaS

---

## Core Principles

### I. Agent-Centric, Event-Driven Architecture
Every feature must be implemented as **independent, single-purpose agents** that communicate through an event bus. No direct inter-agent coupling. Each agent has:
- Clear responsibility boundary
- Capability manifest describing its functions
- Health check endpoint for monitoring
- Ability to hot-swap without system downtime

**Why**: Enables independent scaling, testing, and evolution. Aligns with spec requirements for modularity and future extensibility.

### II. Multi-Tenant SaaS First
Every feature must support multi-tenancy:
- User authentication and authorization enforced at all layers
- Data isolation by tenant (PostgreSQL row-level security)
- Per-user Knuspr credentials stored securely
- Country selection and localization support
- Pricing model: Monthly subscription with usage tracking

**Why**: This is a commercial product. Every architectural decision must assume multiple paying users from different regions.

### III. Anthropic-First AI Integration
All AI/ML features use Anthropic Claude models exclusively:
- Ingredient intelligence powered by Claude
- Recipe analysis and duplicate detection use Claude
- No ML model fine-tuning or custom training in phase 1
- Clear cost accounting for API usage per user
- Fallback strategies when API limits are reached

**Why**: Standardizes AI capabilities, simplifies deployment, leverages best-in-class models.

### IV. Mobile-First Web UI + Optional CLI
Frontend strategy:
- Web UI primary interface (mobile-first responsive design)
- Accessible from phone, tablet, desktop
- Optional CLI for power users (Python-based, FastAPI integration)
- All backend features accessible via both interfaces
- Progressive enhancement: works on mobile even with slow networks

**Why**: Maximizes user accessibility. Mobile-first ensures usability constraints are met from the start.

### V. Performance Measurement from Day One
Every agent and API endpoint must expose performance metrics:
- Prometheus metrics exposed at `/metrics`
- Track: request latency, success rate, queue depth, resource usage
- Alerts configured for degradation (TBD in ops planning)
- Performance baselines established for 10-user baseline
- Future scaling decisions based on measured data, not guesses

**Why**: We don't yet know what "scalable" means for this product. Measurement-driven approach allows confident scaling decisions later.

### VI. PostgreSQL as Single Source of Truth
Data modeling principles:
- All persistent data lives in PostgreSQL (no "eventual consistency" hacks)
- Redis used ONLY for caching and message queuing (cleared without data loss)
- Schema versioning via migrations (Alembic)
- Row-level security policies for tenant isolation
- Indexes planned for common query patterns

**Why**: Simplifies reasoning about data, eliminates distributed state bugs, ensures data integrity for a financial/grocery product.

### VII. Testing as Non-Negotiable Foundation
Testing hierarchy (in order of priority):
1. **Unit tests** for agents (each agent tested in isolation)
2. **Contract tests** for event schemas (Pact or JSON Schema)
3. **Integration tests** for workflows (Puppeteer scrapers, Knuspr API, constraint solver)
4. **End-to-end tests** for full user flows (API + frontend)
5. **Performance tests** at API and agent level (Prometheus dashboards)

**Minimum coverage**: 80% code coverage required; 100% for agent orchestration logic.

**Why**: Multi-agent systems are complex. Tests must verify contracts between agents, not just happy paths.

### VIII. Security by Design
Security requirements:
- Knuspr credentials encrypted at rest (PGP or AES-256)
- User passwords hashed with bcrypt (minimum 12 rounds)
- All API endpoints authenticated (JWT tokens, 1-hour expiry)
- CORS configured for known frontend domains only
- Rate limiting per user (100 requests/minute initially)
- Audit logging for all Knuspr cart operations
- HTTPS enforced for all production traffic

**Why**: This system touches user finances (grocery deliveries). Security cannot be an afterthought.

---

## Technology Stack Principles

### Required Technologies (Non-Negotiable)
- **Agent Orchestration**: LangChain/LangGraph (mandated by spec, proven for multi-agent)
- **Agent Frameworks**: PydanticAI + AtomicAgents (for agent implementation)
- **Python Runtime**: FastAPI backend (async-first for I/O-heavy operations)
- **Database**: PostgreSQL (strict ACID guarantees required)
- **Monitoring**: Prometheus (required for performance measurement principle)
- **Containerization**: Docker (required for agent independence)

### Open Choices (To Be Determined in Planning Phase)
- **Frontend Framework**: React, Vue, or Svelte (mobile-first constraint applies)
- **Constraint Solver**: Z3 vs OR-Tools (performance benchmarks required)
- **Recipe Parser**: Custom Puppeteer vs heuristics vs Claude (cost/quality tradeoff)

### Future-Proofing Decisions
- **Redis Preparation**: Structure code assuming Redis integration for caching (phase 2)
- **Agno/Google ADK**: Evaluate for production deployment (phase 2)
- **Kubernetes**: Design agents for eventual K8s deployment (current: Docker Compose)

---

## Data & Privacy Principles

### User Data Handling
- Minimal data collection: Only what's needed for meal planning and Knuspr integration
- Knuspr credentials never logged or cached outside encrypted storage
- Recipe collections belong to user (can be exported, deleted)
- Deletion requests honored within 30 days (GDPR compliance)
- Usage metrics aggregated and anonymized for product analytics

### Multi-Tenant Data Isolation
- Every query includes tenant ID (user_id)
- PostgreSQL row-level security policies enforce isolation
- Redis keys namespaced by user
- No possibility of serving user A data to user B (tested in contracts)

---

## Agent Architecture Principles

### Agent Design Constraints
1. **Single Responsibility**: Each agent has one core job (harvest, substitute, plan, optimize)
2. **Capability Manifest**: Published at startup, routing decisions based on manifest
3. **Health Checks**: Required for load balancing and failover
4. **Graceful Degradation**: Failure of one agent doesn't crash others
5. **Async Communication**: Event bus prevents blocking, enables scaling

### Agent Types & Boundaries
- **Recipe Harvester Agents**: Web scraping, API integration, RSS parsing
- **Ingredient Intelligence Agents**: Taxonomy lookup, substitution logic, allergen checking
- **Meal Architect Agent**: Constraint satisfaction, weekly planning
- **Cart Optimizer Agents**: Knuspr API integration, delivery slot optimization
- **Support Agents**: Notification service, error handling, user preferences

### Inter-Agent Communication
- **Protocol**: JSON events over event bus (NATS/RabbitMQ in phase 1, Redis for now)
- **Schemas**: Strict JSON Schema validation for every event type
- **Idempotency**: All agent handlers must be idempotent (safe to replay)
- **Correlation IDs**: Trace workflows across agents for debugging

---

## Deployment & Operations Principles

### Phase 1 (MVP - Current)
- Docker Compose for local development and single-server deployment
- PostgreSQL + Redis on localhost or managed service
- FastAPI server with Uvicorn (single or multi-process)
- Prometheus scraping metrics from `/metrics` endpoint
- Manual or simple GitHub Actions for CI/CD

### Phase 2 (Scale-Ready)
- Kubernetes cluster (migration path documented)
- Agno for agent lifecycle management
- Google ADK for infrastructure orchestration
- Multiple replicas of each agent type
- Auto-scaling based on Prometheus metrics

### Production Readiness Checklist
- [ ] Prometheus metrics exposed and dashboards created
- [ ] Error rates and latencies tracked
- [ ] Alerting rules configured for anomalies
- [ ] Backup/recovery procedures documented
- [ ] Tenant isolation security audit completed
- [ ] Load testing completed (10 users baseline)

---

## Quality Gates & Review Process

### All Code Changes Require
1. **Specification alignment**: Feature described in spec before implementation
2. **Test coverage**: Unit + integration tests, minimum 80% coverage
3. **Contract validation**: Event schemas validated, agent interfaces respected
4. **Performance baseline**: No regressions vs. prior measurements
5. **Security review**: For anything touching credentials, payments, or user data

### Agent Changes (Special Rules)
- Capability manifest changes trigger orchestration review
- Event schema changes trigger contract testing
- Deployed agents require health check validation
- Rollback procedure documented before deployment

---

## Measurement & Success Metrics

### Phase 1 Success Criteria (MVP Launch)
- SC-001 through SC-010 from specification (achievable with current setup)
- 10 concurrent users supported (stress tested)
- <5s meal plan generation for typical constraints
- 90%+ Ottolenghi recipe harvesting success rate
- Prometheus dashboard showing all key metrics

### Ongoing Measurement
- Monthly SaaS metrics: User count, churn, feature usage
- Agent metrics: Success rate, latency, cost (Anthropic API calls)
- System metrics: Database size, cache hit rate, error logs
- User feedback: NPS survey, feature requests, bug reports

---

## Governance

### Constitution Authority
This constitution supersedes all other development practices and guidelines. It is the source of truth for architectural and operational decisions.

### Amendment Process
1. Identify need for amendment (specification gap, tech change, lessons learned)
2. Document proposed change with rationale
3. Review with team (if multi-person)
4. Update constitution and ratification date
5. Document migration plan for any breaking changes

### Compliance Verification
- **PR reviewers**: Must verify compliance before merge
- **Automated checks**: Linting, testing, schema validation in CI
- **Manual audits**: Quarterly review of agent implementations vs. constitution

### Decision Log
Decisions documenting:
- What was decided
- Why (principle-based reasoning)
- Who decided
- Date of decision
- Impact on other systems

---

## Phase 1 Scope & Commitments

### In Scope for MVP
- Multi-tenant user management (sign up, login, logout)
- Knuspr integration (MCP + login per user + country selection)
- Recipe harvesting from Ottolenghi (Puppeteer-based)
- Ingredient intelligence (basic rule-based + Claude)
- Weekly meal planning (constraint satisfaction)
- Grocery cart generation (Knuspr integration)
- Web UI (mobile-first, React/Vue TBD)
- Prometheus monitoring + basic dashboards

### Explicitly Out of Scope (Phase 2+)
- Advanced ML recipe parsing (Claude good enough for MVP)
- Multiple grocery store integrations (Knuspr only)
- Offline mode
- Mobile native app (web responsive is sufficient)
- AI recipe generation (discovery/harvesting first)
- Community features (sharing, reviews)
- Advanced nutrition analytics

### Performance Commitments
- Meal plan generation: <5s for 7-day plan
- Cart creation: <2s for typical ingredient list
- Recipe harvesting: <30s per URL (with retries)
- API response times: <200ms for standard queries

---

**Next Steps**: Generate implementation plan and task breakdown from this constitution.

**Custodians**: Product team (David), Lead architect (TBD)

---

*This constitution establishes the guardrails for all feature development. Every design decision, every code review, and every deployment should validate against these principles.*
