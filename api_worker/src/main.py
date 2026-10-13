from workers import asgi

from app.api.main import app

# Reuse the canonical FastAPI application.
Default = asgi.entrypoint(app)
