# Go, Cart! Quickstart Guide

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker (optional, for Qdrant)

## Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Database Setup
1. Create PostgreSQL database: `createdb go_cart`
2. Update `backend/.env` with DB credentials
3. Run migrations: `cd backend && alembic upgrade head`
4. Seed data: `cd backend/scripts && python seed_test_data.py`

## Environment Variables
### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@localhost:5432/go_cart
SECRET_KEY=your-secret-key
KNUSPR_CLIENT_ID=your-client-id
KNUSPR_CLIENT_SECRET=your-client-secret
SENTRY_DSN=your-sentry-dsn
```

### Frontend (.env.local)
```
NEXTAUTH_SECRET=your-secret
NEXTAUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing
```bash
# Backend
cd backend && pytest tests/ -v

# Frontend
cd frontend && npm test
```

## Deployment
- **Backend**: Railway (`railway up`)
- **Frontend**: Vercel (`vercel --prod`)

## Key Features
- AI-powered meal planning with multi-agent workflows
- Knuspr grocery cart integration
- Offline-first waitlist with Service Worker
- 60fps animations (Lenis + GSAP + Framer Motion)
- WCAG 2.1 AAA compliant
- SEO optimized with Open Graph metadata

## API Documentation
Available at `http://localhost:8000/api/docs`