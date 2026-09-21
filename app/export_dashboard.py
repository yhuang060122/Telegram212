import os

from app.exporter import DashboardExporter

db_path = os.getenv(
    "PORTFOLIO_DB",
    "data/portfolio.db"
)

exporter = DashboardExporter(db_path)

file = exporter.export()

print(f"Dashboard exported: {file}")