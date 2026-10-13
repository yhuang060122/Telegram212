from app.api.main import app
from workers import asgi

# Keep all API routes in app/api; this file is only the Cloudflare ASGI adapter.
Default = asgi.entrypoint(app)
