import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analytics, portfolio, research, system

app = FastAPI(
    title="Trading212 AI Analyst API",
    description="Read-only REST API for the Trading212 AI Analyst dashboard.",
    version="1.0.0",
)

origins = [
    origin.strip()
    for origin in os.getenv(
        "DASHBOARD_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(system.router, prefix="/api")
app.include_router(portfolio.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(research.router, prefix="/api")


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "name": "Trading212 AI Analyst API",
        "docs": "/docs",
        "health": "/api/health",
    }
