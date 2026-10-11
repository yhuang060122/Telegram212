import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analytics import router as analytics_router
from app.api.routes.history import router as history_router
from app.api.routes.portfolio import router as portfolio_router
from app.api.routes.positions import router as positions_router
from app.api.routes.reports import router as reports_router

app = FastAPI(
    title="Trading212 AI Analyst API",
    description="Read-only REST API for the Trading212 dashboard",
    version="1.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "DASHBOARD_CORS_ORIGINS", "http://localhost:8080, http://127.0.0.1:8080"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(portfolio_router)
app.include_router(analytics_router)
app.include_router(history_router)
app.include_router(positions_router)
app.include_router(reports_router)


@app.get("/api/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "trading212-ai-analyst-api",
    }
