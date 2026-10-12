from fastapi import FastAPI
from workers import asgi

app = FastAPI(
    title="Trading212 AI Analyst API",
    version="1.0.0",
)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service": "telegram212-api",
    }


@app.get("/api/portfolio")
async def portfolio():
    # 下一步接入现有 Repository
    return {
        "status": "not_implemented",
        "message": "Repository integration pending",
    }


Default = asgi.entrypoint(app)
