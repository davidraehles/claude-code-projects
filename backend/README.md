Docker build notes
------------------

This directory contains the Dockerfile for the backend service.

Build tips
- To build using the backend folder as the build context (common for local development):

```bash
cd backend
docker build -t meal-planner-backend:local .
```

- To build from the repository root (this is what Railway uses by default):

```bash
docker build -f backend/Dockerfile -t meal-planner-backend:local .
```

Why this matters
- Some CI/CD systems (like Railway) set the build context to the repository root while pointing
  the Dockerfile to a subdirectory. The `COPY` source paths in the Dockerfile must therefore
  match the chosen build context. The `backend/Dockerfile` has been updated to reference
  `backend/alembic.ini` explicitly to avoid failures when the context is the repo root.
