# Technology Transition Guide

**Document Type**: Internal Implementation Guide
**Version**: 1.0.0
**Date**: 2025-11-14
**Purpose**: Explain phased technology choices and migration pathways

---

## Overview

This document explains why certain technologies are used in **Phase 1 (MVP)** versus **Phase 2+ (Production Scaling)**, and provides migration strategies for upgrading components without breaking the system.

### Core Philosophy

> **"Start simple, scale when needed"**

Phase 1 prioritizes:
- Fast time-to-market
- Developer productivity
- Minimal operational overhead
- Clear upgrade paths

Phase 2+ prioritizes:
- Production scale (100+ users)
- High availability
- Advanced features
- Infrastructure efficiency

---

## 1. Event Bus Technology Transition

### Phase 1: Redis Pub/Sub or FastAPI Background Tasks

**Why This Choice?**
- ✅ **Simplicity**: Redis Pub/Sub is part of standard Docker Compose stack
- ✅ **Low overhead**: No separate broker infrastructure
- ✅ **Good enough for MVP**: Handles 10 concurrent users easily
- ✅ **Familiar**: Redis already used for caching
- ✅ **Fast prototyping**: Minimal setup, immediate testing

**Limitations (Why We Upgrade Later)**
- ❌ **No persistence**: Messages lost if Redis crashes
- ❌ **No durability guarantees**: Fire-and-forget semantics
- ❌ **No ordering**: Messages may arrive out of order (minor issue)
- ❌ **Scalability**: Single Redis instance can't handle 1000+ msg/sec
- ❌ **No routing flexibility**: Pub/Sub topic matching is simplistic

**Implementation**:
```python
# src/events/bus.py (Phase 1)
class EventBus:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def publish(self, event: Event):
        """Publish event to Redis Pub/Sub"""
        topic = event.eventType.split('.')[0]  # e.g., "recipe" from "recipe.harvest.requested"
        await self.redis.publish(topic, event.json())

    async def subscribe(self, topic: str, handler: Callable):
        """Subscribe to topic pattern"""
        pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        await pubsub.psubscribe(f"{topic}.*")
        async for message in pubsub.listen():
            event = Event.parse_raw(message['data'])
            await handler(event)
```

**Phase 1 Limitations to Document**:
- Document in code comments: "Phase 1 MVP only - upgrade in Phase 2"
- Test with 100 events/sec (sufficient for 10 users)
- Monitor Redis memory usage
- Set up alerts for queue depth

### Phase 2: RabbitMQ or Redis Streams

**Why This Upgrade?**
- ✅ **Persistence**: Messages survive crashes
- ✅ **Durability guarantees**: At-least-once delivery semantics
- ✅ **Message ordering**: Guarantees FIFO within streams
- ✅ **Routing flexibility**: Advanced topic matching and filtering
- ✅ **Scalability**: Handles 1000+ msg/sec easily
- ✅ **Clustering**: Built-in HA and replication

**Technology Choice Decision**:
- **RabbitMQ**: If you want traditional message broker (proven, battle-tested)
- **Redis Streams**: If you want minimal new dependencies (Redis already deployed)

**Recommended**: Redis Streams (less operational overhead, same Redis dependency)

**Migration Path (Phase 1 → Phase 2)**:

```
Phase 1 Code:
├── EventBus uses Redis Pub/Sub
├── Events published with .json() serialization
└── Handlers are async functions

Phase 2 Code:
├── EventBus uses Redis Streams
├── Same event serialization format
├── Same async handler interface
└── Drop-in replacement (minimal code changes)

Benefits:
- Event schema doesn't change
- Handler signatures remain identical
- No client code changes needed
- Can test with Stream locally before production
```

**Implementation Strategy**:

```python
# src/events/bus.py (Phase 2)
class EventBus:
    def __init__(self, redis_client, use_streams=True):
        self.redis = redis_client
        self.use_streams = use_streams

    async def publish(self, event: Event):
        """Publish event with dual-write support during migration"""
        if self.use_streams:
            # Phase 2: Streams for durability
            await self.redis.xadd(
                f"stream:{event.eventType.split('.')[0]}",
                {"data": event.json()}
            )
        else:
            # Phase 1: Pub/Sub for simplicity
            await self.redis.publish(
                event.eventType.split('.')[0],
                event.json()
            )

    # Handlers work identically - no change needed
```

**Migration Timeline**:
- **Week N**: Deploy Phase 2 with Streams alongside Pub/Sub
- **Week N+1**: Dual-write test (publish to both, consume from Streams)
- **Week N+2**: Migrate consumers to Stream handlers one-by-one
- **Week N+3**: Turn off Pub/Sub, monitor for issues
- **Week N+4**: Remove Pub/Sub code

---

## 2. Database Deployment Transition

### Phase 1: Docker Compose (Single PostgreSQL Container)

**Why This Choice?**
- ✅ **Simplicity**: One container, obvious deployment
- ✅ **Local development**: Run entire stack locally
- ✅ **Sufficient for MVP**: Single container handles 10 concurrent users
- ✅ **Data persistence**: Docker volumes ensure data survives restarts
- ✅ **No managed service cost**: Pure open-source

**Limitations**
- ❌ **Single point of failure**: One container = complete data loss if corrupt
- ❌ **No backups**: Manual backup required
- ❌ **No replication**: Single read/write endpoint
- ❌ **No managed upgrades**: Manual PostgreSQL upgrades

**Docker Compose Configuration**:
```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: recipes
      POSTGRES_USER: recipes_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U recipes_user"]
      interval: 10s
```

### Phase 2: Managed Database Service

**Why This Upgrade?**
- ✅ **High Availability**: Automatic failover, replicas
- ✅ **Backups**: Automated, tested recovery
- ✅ **Scaling**: Increase resources without downtime
- ✅ **Monitoring**: Built-in performance insights
- ✅ **Security**: Encryption at rest, managed TLS

**Technology Choices**:
- **AWS RDS**: If on AWS infrastructure
- **Google Cloud SQL**: If on Google Cloud
- **Azure Database**: If on Microsoft Azure
- **Heroku Postgres**: If on Heroku platform
- **Self-managed Kubernetes**: If using K8s (Phase 2+ only)

**Migration Path (Phase 1 → Phase 2)**:

```
Phase 1:
├── Docker Compose PostgreSQL
├── Data in docker-compose_postgres_data volume
└── No backups (manual only)

Phase 2:
├── Managed RDS or Cloud SQL
├── Data restored from final Phase 1 backup
├── Same Alembic migrations apply
└── Same application code works (connection string change only)

Zero-downtime migration:
1. Full backup of Phase 1 database
2. Create managed database with same schema
3. Restore backup data
4. Test connections
5. Update environment variable: DATABASE_URL=new_managed_db
6. Deploy application
7. Monitor for issues
```

**Connection String Change**:
```python
# Phase 1 (local)
DATABASE_URL=postgresql://recipes_user:password@postgres:5432/recipes

# Phase 2 (managed RDS)
DATABASE_URL=postgresql://recipes_user:password@recipes-db.xxx.rds.amazonaws.com:5432/recipes

# No code change needed - same format!
```

---

## 3. Production Deployment Transition

### Phase 1: Docker Compose (Single Server)

**Why This Choice?**
- ✅ **Simplicity**: One `docker-compose up` command
- ✅ **Low cost**: Single small server (~$10-20/month)
- ✅ **Full control**: Direct SSH access
- ✅ **Debugging**: Logs directly visible

**Deployment Steps**:
```bash
# Phase 1: Manual deployment to single server
1. SSH into production server
2. git pull origin main
3. docker-compose build
4. docker-compose down
5. docker-compose up -d
6. docker-compose exec fastapi alembic upgrade head
7. Verify health checks: curl /health
```

**Limitations**:
- ❌ **No load balancing**: Single server = single point of failure
- ❌ **No auto-scaling**: Manual server management
- ❌ **Manual deployments**: Downtime during updates
- ❌ **Limited monitoring**: Basic host-level metrics only

### Phase 2: Kubernetes + Agno/Google ADK

**Why This Upgrade?**
- ✅ **High availability**: Multiple replicas, auto-failover
- ✅ **Auto-scaling**: Respond to traffic spikes automatically
- ✅ **Zero-downtime deployments**: Rolling updates
- ✅ **Self-healing**: Automatic restart of failed pods
- ✅ **Infrastructure as code**: Version control for deployment

**Technology Stack**:
- **Kubernetes**: Container orchestration (Docker Swarm alternative: simpler but less flexible)
- **Agno**: LangChain deployment framework (optional, depends on availability)
- **Google ADK**: Google Cloud deployment tools (optional)

**Migration Path (Phase 1 → Phase 2)**:

```
Phase 1: Docker Compose
├── Single FastAPI container
├── Single PostgreSQL container
└── Single Redis container

Phase 2: Kubernetes
├── Multiple FastAPI pods (auto-scaled)
├── Managed PostgreSQL (RDS/Cloud SQL)
├── Managed Redis (ElastiCache/Cloud Memorystore)
├── Ingress controller (Nginx/AWS ALB)
└── Service mesh (optional, Istio/Linkerd)

Code Changes Required:
- None! Same Docker images
- Same application code
- Same environment variables
- Only deployment configuration changes
```

**Kubernetes Manifest Example**:
```yaml
# k8s/deployment.yaml (Phase 2)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recipes-api
spec:
  replicas: 3  # Auto-scaled by HPA
  selector:
    matchLabels:
      app: recipes-api
  template:
    metadata:
      labels:
        app: recipes-api
    spec:
      containers:
      - name: recipes-api
        image: recipes:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: redis-config
              key: url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Deployment Strategy**:
```
Week 1: Kubernetes Learning
- Set up local Minikube cluster
- Deploy Docker Compose images to K8s
- Practice rolling updates

Week 2: Production K8s Setup
- Create managed K8s cluster (GKE, EKS, AKS)
- Deploy secrets and configmaps
- Set up ingress controller

Week 3: Agno/Google ADK Integration
- Evaluate Agno deployment features
- Test agent deployment in K8s pods
- Document agent scaling patterns

Week 4: Migration
- Deploy Phase 2 to K8s alongside Phase 1
- Test traffic routing
- Gradual traffic shift (10% → 50% → 100%)
- Monitor and rollback if needed
- Decommission Phase 1 Docker Compose
```

---

## 4. Constraint Solver Transition

### Phase 1: Z3 (Python Library)

**Why This Choice?**
- ✅ **Simplicity**: Pure Python, pip install
- ✅ **Powerful**: Handles complex constraints
- ✅ **Good performance**: <5 seconds for 7-day plans (our target)
- ✅ **No external service**: Zero network latency
- ✅ **Proven**: Used in production systems

**Implementation Pattern**:
```python
# src/agents/meal_architect.py (Phase 1)
from z3 import *

def generate_meal_plan(constraints):
    solver = Solver()

    # Define variables and constraints
    recipes = [recipe_1, recipe_2, ..., recipe_n]
    selected_recipes = [Bool(f"recipe_{i}") for i in range(len(recipes))]

    # Add constraints
    solver.add(PK.AtLeast(*selected_recipes, 7))  # Exactly 7 meals
    solver.add(PK.AtMost(*selected_recipes, 7))

    # Solve
    if solver.check() == sat:
        model = solver.model()
        return extract_solution(model)
```

**Limitations**:
- ❌ **Single-core**: Can't parallelize across cores easily
- ❌ **In-process**: Blocks FastAPI while solving
- ❌ **Limited scaling**: Harder as recipe database grows (1000+ recipes)

### Phase 2: OR-Tools (Google Optimization)

**Why This Upgrade?**
- ✅ **Better performance**: Often 10-100x faster than Z3
- ✅ **Parallelization**: Multi-core solver support
- ✅ **Scalability**: Handles larger problem sizes efficiently
- ✅ **Routing**: Built-in vehicle routing (future feature)
- ✅ **Benchmarking**: Extensive research behind Google's solver

**Migration Path**:

```python
# Abstract solver interface (Phase 1 & 2)
class MealPlanSolver(ABC):
    @abstractmethod
    async def solve(self, constraints: MealPlanConstraints) -> MealPlan:
        pass

# Phase 1 Implementation
class Z3MealPlanSolver(MealPlanSolver):
    async def solve(self, constraints):
        # ... Z3 logic ...
        pass

# Phase 2 Implementation
class ORToolsMealPlanSolver(MealPlanSolver):
    async def solve(self, constraints):
        # ... OR-Tools logic ...
        pass

# Application uses solver via interface
class MealArchitectAgent:
    def __init__(self, solver: MealPlanSolver):
        self.solver = solver

    async def generate_plan(self, constraints):
        return await self.solver.solve(constraints)
```

**Migration Strategy**:
```
Phase 2 Week N:
1. Implement OR-Tools solver alongside Z3
2. Add feature flag: MEAL_PLAN_SOLVER=z3|ortools
3. A/B test both solvers
4. Compare performance: latency, memory, result quality
5. If OR-Tools 10%+ faster: gradual rollout (10% → 50% → 100%)
6. If Z3 good enough: defer to Phase 3+
7. Monitor solution quality metrics
```

**Benchmarking**:
```python
# benchmark_solvers.py
import time
from z3_solver import Z3MealPlanSolver
from ortools_solver import ORToolsMealPlanSolver

solvers = {
    "z3": Z3MealPlanSolver(),
    "ortools": ORToolsMealPlanSolver()
}

for solver_name, solver in solvers.items():
    times = []
    for _ in range(10):
        start = time.time()
        result = solver.solve(typical_constraints)
        times.append(time.time() - start)

    print(f"{solver_name}: avg {sum(times)/len(times):.2f}s, min {min(times):.2f}s, max {max(times):.2f}s")

# Expected output:
# z3: avg 2.34s, min 2.10s, max 2.88s
# ortools: avg 1.12s, min 0.95s, max 1.45s (faster!)
```

---

## 5. Notification Service Transition

### Phase 1: In-App Notifications Only

**Why This Choice?**
- ✅ **Simplicity**: No external dependencies
- ✅ **Privacy**: No email/SMS data shared
- ✅ **Fast**: Network latency is minimal
- ✅ **Sufficient for MVP**: Users check app regularly

**Implementation**:
```python
# src/services/notification.py (Phase 1)
class NotificationService:
    async def create_notification(self, user_id: int, notification: NotificationCreate):
        """Create in-app notification"""
        db_notification = Notification(
            user_id=user_id,
            type=notification.type,  # "info", "warning", "error", "success"
            title=notification.title,
            message=notification.message,
            action_url=notification.action_url,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        await self.db.notifications.insert(db_notification)

        # Emit event for real-time delivery (WebSocket in Phase 2)
        await self.event_bus.publish(NotificationCreated(notification=db_notification))

# API endpoint
@router.get("/notifications")
async def list_notifications(current_user = Depends(get_current_user)):
    """Get unread notifications for current user"""
    return await db.notifications.find(
        user_id=current_user.id,
        read_at=None,
        order_by="created_at DESC"
    )
```

### Phase 2: Email + SMS Notifications

**Why This Upgrade?**
- ✅ **Retention**: Users receive notifications even if app not open
- ✅ **Engagement**: Email digests drive daily active users
- ✅ **Preference control**: Users choose notification channels
- ✅ **Business metrics**: Track email open rates, SMS delivery

**Technology Stack**:
- **Email**: SendGrid (transactional) + Mailgun (bulk)
- **SMS**: Twilio or AWS SNS
- **Push notifications**: Firebase Cloud Messaging (optional)

**Migration Path**:

```python
# Notification interface (Phase 1 & 2)
class NotificationChannel(ABC):
    @abstractmethod
    async def send(self, user: User, message: str) -> bool:
        pass

# Phase 1: In-app only
class InAppChannel(NotificationChannel):
    async def send(self, user: User, message: str) -> bool:
        await db.notifications.insert(...)
        return True

# Phase 2: Multiple channels
class EmailChannel(NotificationChannel):
    async def send(self, user: User, message: str) -> bool:
        response = await sendgrid.send(to=user.email, message=message)
        return response.status == 202

class SMSChannel(NotificationChannel):
    async def send(self, user: User, message: str) -> bool:
        response = await twilio.sms.create(to=user.phone, message=message)
        return response.status == "sent"

# Application uses channels via strategy pattern
class MultiChannelNotificationService:
    async def send(self, user: User, notification: Notification):
        channels = []
        if user.preferences.notifications.in_app:
            channels.append(InAppChannel())
        if user.preferences.notifications.email:
            channels.append(EmailChannel())
        if user.preferences.notifications.sms:
            channels.append(SMSChannel())

        results = await asyncio.gather(
            *[channel.send(user, notification.message) for channel in channels]
        )
        return all(results)
```

---

## 6. Frontend Framework Transition

### Phase 1: React 18 or Vue 3 (TBD)

**Decision Gate**: Choose framework based on:
- Team expertise
- Community size for component libraries
- Build tool preferences (Vite vs Create React App)

**Implementation**:
```
Phase 1: Mobile-first React/Vue
├── HTML responsive design (no CSS-in-JS complexity)
├── Tailwind CSS for styling
├── Zustand/Pinia for state management
├── TanStack Query for API caching
└── Vite for fast builds
```

### Phase 2: Native Mobile Apps (Optional)

**Technology Choice**:
- **React Native**: If chose React for web (code sharing)
- **Flutter**: If want best performance and design
- **SwiftUI/Kotlin**: If need app store features

**Phase Recommendation**: Defer until 100+ users (justify development cost)

---

## Technology Debt Tracking

### Create an ADR Log

Document each technology decision with:
```markdown
# ADR-001: Choose Redis Pub/Sub for Phase 1 Event Bus

**Status**: Accepted (Phase 1), Revision Planned (Phase 2)
**Date**: 2025-11-14
**Deciders**: Technical team

## Decision
Use Redis Pub/Sub for Phase 1 event bus, upgrade to RabbitMQ/Redis Streams in Phase 2

## Rationale
- Redis already in stack (no new dependency)
- 10 users = <100 msg/sec (well within limits)
- Simple API reduces learning curve
- Easy to upgrade later (handler interface unchanged)

## Phase 2 Upgrade Plan
- Week 32: Implement Redis Streams alongside Pub/Sub
- Week 33-34: Dual-write testing
- Week 35: Gradual consumer migration
- Week 36: Remove Pub/Sub code

## Consequences
- ✅ Fast Phase 1 delivery
- ❌ Must plan Phase 2 upgrade early
- ❌ No message persistence (document limitation)
- ✅ Clear upgrade path documented
```

---

## Checklist for Phase 1 → Phase 2 Migration

### Before Starting Phase 2:

- [ ] Document all Phase 1 technology trade-offs in ADR format
- [ ] Create branch: `feature/phase-2-infrastructure-upgrade`
- [ ] Plan upgrade in 2-week sprints (one technology per sprint)
- [ ] Set up feature flags for A/B testing upgrades
- [ ] Create runbooks for each upgrade scenario
- [ ] Plan rollback procedures for each upgrade
- [ ] Set up separate staging environment with Phase 2 tech

### During Phase 2 Development:

- [ ] Keep Phase 1 tech operational until fully replaced
- [ ] Dual-write patterns during data migration
- [ ] Comprehensive integration testing
- [ ] Performance benchmarking of new tech
- [ ] Gradual traffic shift (10% → 25% → 50% → 100%)
- [ ] 24/7 monitoring during transitions
- [ ] Quick rollback capability at every step

### Post-Migration:

- [ ] Remove Phase 1 technology
- [ ] Update documentation
- [ ] Document lessons learned
- [ ] Plan Phase 3 technologies
- [ ] Archive ADRs and migration logs

---

## Technology Evolution Timeline

```
Phase 1 (Weeks 1-4): MVP Foundation
├── Docker Compose (single server)
├── Redis Pub/Sub
├── PostgreSQL local
├── Z3 solver
├── In-app notifications
└── React/Vue (TBD)

Phase 2 (Weeks 5-8): Production Ready
├── Kubernetes cluster
├── Redis Streams
├── Managed PostgreSQL
├── Z3 or OR-Tools (benchmarked)
├── Email/SMS notifications
└── Native mobile app planning

Phase 3+ (Weeks 9+): Advanced Features
├── Microservices (if needed)
├── GraphQL API
├── Real-time WebSocket
├── Machine learning pipeline
├── Advanced analytics
└── Marketplace features
```

---

## Key Principles for Tech Transitions

1. **Interface Abstraction**: Always use interfaces/abstract classes, not concrete implementations
2. **Feature Flags**: Control old vs new technology via runtime flags
3. **Dual Write**: Write to both old and new during migration
4. **Comprehensive Tests**: Test both old and new implementations identically
5. **Gradual Rollout**: Never flip all traffic at once (10% → 50% → 100%)
6. **Monitoring**: Monitor both old and new during parallel operation
7. **Rollback Plan**: Every migration must have a 5-minute rollback procedure
8. **Documentation**: Document why Phase 1 choice was made, not just what it is

---

**This guide ensures smooth technology evolution without blocking product development.**

For questions about specific transitions, see the relevant Architecture Decision Record (ADR) in `docs/adr/`.
