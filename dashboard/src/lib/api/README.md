# API client (Phase 5.6)

The dashboard talks **only** to the Python FastAPI backend. It never talks to Supabase directly.
The Supabase service role key and other credentials belong **only** in the backend's environment. Never put them in `VITE_*` variables, because those are shipped to the browser.

## Configure

```bash
# .env.local
VITE_API_BASE_URL=http://127.0.0.1:8000   # default if unset; trailing slash is stripped
```

## Endpoints

| Function | Path | Hook | Cache |
|---|---|---|---|
| `api.getHealth` | `GET /api/health` | `useApiHealthQuery` / `useApiConnection` | 30s, polls 1m |
| `api.getPortfolio` | `GET /api/portfolio` | `usePortfolioQuery` | 1m, polls 5m |
| `api.getPositions` | `GET /api/positions` | `usePositionsQuery` | 1m, polls 5m |
| `api.getHistory(days)` | `GET /api/history?days=365` | `useHistoryQuery(days)` | 15m |
| `api.getPositionHistory(t)` | `GET /api/positions/{ticker}/history` | `usePositionHistoryQuery(t)` (disabled when empty) | 15m |
| `api.getMonthlyReturns` | `GET /api/monthly-returns` | `useMonthlyReturnsQuery` | 60m |
| `api.getAnalytics` | `GET /api/analytics` | `useAnalyticsQuery` | 15m |
| `api.getLatestReport` | `GET /api/report/latest` | `useLatestReportQuery` | 30m |
| `api.getNews` | `GET /api/news` | `useNewsQuery` | 10m, polls 15m |
| `api.getEarnings(days)` | `GET /api/earnings?days=30` | `useEarningsQuery(days)` | 60m |
| `api.getLatestMacro` | `GET /api/macro/latest` | `useLatestMacroQuery` | 60m |

Refresh: `useDashboardRefresh()()` invalidates everything under `queryKeys.all`; pass key groups to refresh a subset.

## Local backend

```bash
uvicorn app.main:app --reload --port 8000
```

## Troubleshooting

- `ApiError.status === 0`: the browser could not reach the backend. This usually means it is not running or CORS is blocking it. Add the dashboard origin (e.g. `http://localhost:8080`, `https://yhuang060122.github.io`) to FastAPI's `CORSMiddleware` `allow_origins`.
- An HTTPS page (GitHub Pages) cannot call an `http://` backend because browsers block mixed content. Use an HTTPS backend URL in production.
- `ApiError.detail` holds the parsed body. `requestId` holds the value of `X-Request-ID` when the backend sends it.

## Phase 5.7 migration path

`src/lib/overview-source.ts` is still demo-only (`isDemo: true`). To go live:
1. Add a mapper `src/lib/api/mappers/overview.ts` that converts the `Portfolio`, `Analytics`, `History`, `Positions`, `Report` and `Health` responses into `OverviewData`. All derivation goes here, never in components.
2. In `Overview.tsx`, replace `overviewSource.getOverview()` with the hooks plus the mapper, and fall back to demo data (keeping the "Demo data" badge) when `useApiConnection().state === "offline"`.
3. Only show "live" when the data actually came from the backend.
