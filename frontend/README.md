# ClaimGuard Frontend

React frontend for the Django claim upload API.

## Run locally

1. Install dependencies:

```bash
npm install
```

2. Start the Django backend on `http://127.0.0.1:8000`.
3. Start the frontend:

```bash
npm run dev
```

The Vite dev server proxies `/api/*` requests to the backend automatically.

## Environment

Use `frontend/.env.example` if you want to point the frontend at a different API origin:

```bash
VITE_API_BASE_URL=https://your-api.example.com
```
