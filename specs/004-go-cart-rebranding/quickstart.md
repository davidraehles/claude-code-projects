# Quickstart: Go, Cart! Frontend

## Prerequisites

- Node.js 18+
- Python 3.11+ (for backend)
- PostgreSQL 15+

## Setup

1. **Initialize Frontend Project**
   ```bash
   # From repo root
   cd frontend
   npm install
   ```

2. **Environment Variables**
   Copy `.env.example` to `.env.local`:
   ```bash
   cp .env.example .env.local
   ```
   Required variables:
   - `NEXT_PUBLIC_API_URL`: URL of the FastAPI backend (default: `http://localhost:8000`)
   - `NEXT_PUBLIC_WAITLIST_ENABLED`: `true`

3. **Run Development Server**
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000) to view the landing page.

## Design System Implementation

### Tailwind Configuration
The design tokens are mapped in `frontend/tailwind.config.ts`.
- **Colors**: Use `bg-primary-500`, `text-secondary-800`, etc.
- **Typography**: Use `font-display` for headings, `font-body` for text.

### Component Library
Located in `frontend/src/components/ui`.
- **Buttons**: `<Button variant="primary">`
- **Inputs**: `<Input error={errors.email} />`

### Icons & Assets
- **Logos**: SVG definitions are located in `specs/004-go-cart-rebranding/svg-logos.xml`. Use these paths for the `Logo` component.
- **Icons**: Use `lucide-react` for standard UI icons.

## Backend Integration

1. **Start Backend**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Verify API**
   Check `http://localhost:8000/docs` for the new `/api/v1/waitlist` endpoints.
