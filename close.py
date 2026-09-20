from app.pipeline import DailyPipeline
import os

DB_PATH = os.getenv(
    "PORTFOLIO_DB",
    "data/portfolio.db"
)

pipeline = DailyPipeline(DB_PATH)

portfolio, report = pipeline.run()

print("Market close snapshot saved.")