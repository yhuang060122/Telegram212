# Dashboard REST API

The dashboard must call this Python API; it must not connect directly to Supabase. The API reuses the existing Repository and AnalyticsService.

## Run locally

Install dependencies and configure the same server-side environment variables used by the backend:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`

Start the API from the repository root:

```powershell
uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000
```

Interactive docs: http://127.0.0.1:8000/docs

For a Vite dashboard running on port 5173, the default CORS allowlist is already configured. To override it, set `DASHBOARD_CORS_ORIGINS` to a comma-separated list of exact origins.

## Read endpoints

| Method | Endpoint | Source |
|---|---|---|
| GET | `/api/health` | Repository health check |
| GET | `/api/portfolio` | Latest snapshot + latest positions |
| GET | `/api/positions` | Latest positions |
| GET | `/api/positions/{ticker}/history` | Position history |
| GET | `/api/history?days=365` | Latest N snapshots, chronological |
| GET | `/api/monthly-returns` | Repository monthly returns |
| GET | `/api/analytics` | Existing AnalyticsService + repository history/cashflows |
| GET | `/api/report/latest` | Latest Pydantic Report |
| GET | `/api/news` | Today's news |
| GET | `/api/earnings?days=30` | Upcoming earnings |
| GET | `/api/macro/latest` | Latest macro snapshot |

The API is read-only and currently has no authentication. Keep it on a trusted network until an authentication layer is added. Never expose `SUPABASE_SERVICE_KEY` to the browser or Vite environment.
