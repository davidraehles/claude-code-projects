# Project Architecture Blueprint

**Generated:** December 15, 2025
**Project Type:** Hybrid (Python FastAPI Backend + Next.js React Frontend)
**Architecture Pattern:** Service-Oriented / Layered Monorepo

---

## 1. Architecture Detection and Analysis

The project is a modern full-stack application structured as a monorepo with distinct separation of concerns:

*   **Backend**: Python 3.11+ using **FastAPI** for the REST API. It leverages **SQLAlchemy** (Async) for ORM, **Pydantic** for data validation, and **LangGraph** for agentic workflows.
*   **Frontend**: **Next.js 16** (App Router) with **React 19**. It uses **Tailwind CSS** for styling and **React Query** for state management.
*   **Infrastructure**: Containerized using **Docker Compose**, with **PostgreSQL** as the primary database and **Redis** for caching/event bus.
*   **Testing**: **Pytest** for backend, **Jest** and **Playwright** for frontend.

## 2. Architectural Overview

The system follows a **Service-Oriented Architecture (SOA)** within a monorepo. The backend and frontend are decoupled, communicating primarily via RESTful APIs.

*   **Guiding Principles**:
    *   **Separation of Concerns**: Clear boundaries between UI, business logic, and data access.
    *   **Async First**: Extensive use of Python's `asyncio` and React's concurrent features.
    *   **Type Safety**: Strict typing in both Python (Type Hints + Pydantic) and TypeScript.
    *   **Agentic Workflow**: Integration of AI agents (LangGraph) for complex tasks like meal planning.

## 3. Architecture Visualization

### High-Level Component Interaction

```mermaid
graph TD
    User[User Browser] -->|HTTPS| Frontend[Next.js Frontend]
    Frontend -->|REST API| Backend[FastAPI Backend]
    Backend -->|SQL| DB[(PostgreSQL)]
    Backend -->|Pub/Sub| Redis[(Redis)]
    Backend -->|Agent Workflow| AI[LangGraph Agents]
    AI -->|External API| External[External Services (Grocery/Recipe)]
```

### Data Flow
1.  **Request**: User initiates action (e.g., "Generate Meal Plan").
2.  **Frontend**: Next.js handles the UI, calls Backend API via React Query.
3.  **Backend API**: FastAPI receives request, validates input (Pydantic).
4.  **Service Layer**: Orchestrates logic. For complex tasks, delegates to **LangGraph Agents**.
5.  **Data Access**: SQLAlchemy interacts with PostgreSQL.
6.  **Response**: Data returned to Frontend, UI updates.

## 4. Core Architectural Components

### Backend (FastAPI)
*   **Purpose**: Core business logic, API endpoints, data management, AI agent orchestration.
*   **Structure**:
    *   `app/main.py`: Entry point, middleware setup.
    *   `app/api/`: Route handlers (Controllers).
    *   `app/services/`: Business logic.
    *   `app/agents/`: AI Agent definitions (LangGraph).
    *   `app/models/`: SQLAlchemy ORM models.
    *   `app/schemas/`: Pydantic DTOs.
*   **Interaction**: Exposes REST endpoints. Consumes DB and Redis.

### Frontend (Next.js)
*   **Purpose**: User interface, client-side routing, state management.
*   **Structure**:
    *   `app/`: App Router pages and layouts.
    *   `components/`: Reusable UI components (Shadcn/UI based).
    *   `lib/`: Utilities and API clients.
    *   `hooks/`: Custom React hooks.
*   **Interaction**: Consumes Backend API.

### Database (PostgreSQL)
*   **Purpose**: Persistent storage for users, recipes, meal plans.
*   **Evolution**: Managed via **Alembic** migrations.

## 5. Architectural Layers and Dependencies

### Backend Layers
1.  **Presentation Layer (API)**: `app/api/`. Handles HTTP requests/responses. Depends on Service Layer.
2.  **Service/Agent Layer**: `app/services/`, `app/agents/`. Contains business logic. Depends on Data Access Layer.
3.  **Data Access Layer**: `app/database.py`, `app/models/`. Handles DB interactions.
4.  **Domain Layer**: `app/schemas/`. Shared data structures (Pydantic).

### Frontend Layers
1.  **UI Layer**: Components and Pages.
2.  **State/Data Layer**: React Query hooks, Context.
3.  **Infrastructure Layer**: API clients (`fetch` wrappers).

## 6. Data Architecture

*   **ORM**: SQLAlchemy 2.0 (Async) is used for database abstraction.
*   **Schema**: Pydantic V2 models define the data shape for API contracts and internal validation.
*   **Migrations**: Alembic handles schema evolution.
*   **Caching**: Redis is used for caching expensive operations and as an event bus for agents.

## 7. Cross-Cutting Concerns

*   **Authentication**: JWT-based auth (likely `python-jose` or `NextAuth.js` integration).
*   **Error Handling**:
    *   Backend: Global exception handlers in FastAPI, mapping exceptions to standardized JSON error responses.
    *   Frontend: Error boundaries and toast notifications.
*   **Logging**: Structured JSON logging (`python-json-logger`) in Backend.
*   **Monitoring**: Sentry integration for error tracking. Prometheus metrics exposed.
*   **Validation**:
    *   Input: Pydantic (Backend), Zod (Frontend).
    *   Strict typing ensures data integrity across boundaries.

## 8. Service Communication Patterns

*   **Synchronous**: REST API (JSON) for most user interactions.
*   **Asynchronous**: Background tasks and Agent workflows managed via internal queues or Redis.
*   **API Versioning**: Likely URL-based (e.g., `/api/v1/`).

## 9. Technology-Specific Patterns

### Python / FastAPI
*   **Dependency Injection**: Extensive use of FastAPI's `Depends` for injecting DB sessions, services, and current user.
*   **Async/Await**: Fully asynchronous request handling for high concurrency.
*   **Middleware**: Custom middleware for Request ID, Correlation ID, and Logging.

### React / Next.js
*   **Server Components**: Leveraging Next.js App Router for server-side rendering where appropriate.
*   **Client Components**: Used for interactive elements (`'use client'`).
*   **Hooks Pattern**: Logic encapsulated in custom hooks (`useMealPlan`, etc.).

## 10. Implementation Patterns

*   **Repository Pattern**: (Implicit or Explicit) Encapsulating DB queries.
*   **DTO Pattern**: Pydantic models separate API contract from DB models.
*   **Composition**: React components built using composition (Slots, Children).

## 11. Testing Architecture

*   **Backend**:
    *   **Unit**: `pytest` for individual functions/services.
    *   **Integration**: `pytest` with test DB containers.
*   **Frontend**:
    *   **Unit**: `jest` + `react-testing-library`.
    *   **E2E**: `playwright` for full user journey testing.

## 12. Deployment Architecture

*   **Containerization**: Dockerfiles for both Backend and Frontend.
*   **Orchestration**: Docker Compose for local dev.
*   **Cloud**: Railway (Backend/DB) and Vercel (Frontend) as per documentation.
*   **CI/CD**: GitHub Actions (implied).

## 13. Extension and Evolution

*   **New Features**:
    *   Backend: Add new Router -> Service -> Model.
    *   Frontend: Add new Route -> Page -> Component.
*   **Agents**: New capabilities added as new nodes in the LangGraph.

## 14. Architecture Governance

*   **Linting**: `flake8`, `black`, `mypy` (Backend); `eslint`, `prettier` (Frontend).
*   **Pre-commit**: Likely used to enforce standards before commit.
*   **Documentation**: `docs/` folder contains architectural decisions and guides.

