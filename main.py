from app.pipeline import DailyPipeline
from app.telegram.bot import TelegramBot
from app.telegram.formatter import Formatter
import os

DB_PATH = os.getenv(
    "PORTFOLIO_DB",
    "data/portfolio.db"
)

def main():

    pipeline = DailyPipeline(DB_PATH)

    portfolio, report, history = pipeline.run()

    bot = TelegramBot()

    message = Formatter.daily(
        portfolio,
        report
    )

    bot.send(message)

    print("✅ Daily report sent.")

if __name__ == "__main__":
    main()