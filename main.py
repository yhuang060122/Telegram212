from app.pipeline import DailyPipeline
from app.telegram.bot import TelegramBot
from app.telegram.formatter import Formatter
from app.supabase_database import SupabaseDatabase

from app.logger import log

def main():

    db = SupabaseDatabase()

    if not db.health_check():
        raise RuntimeError("Supabase connection failed")

    pipeline = DailyPipeline()

    portfolio, report, history = pipeline.run()

    message = Formatter.daily(
        portfolio,
        report
    )

    TelegramBot().send(message)

    log.success(
        "Telegram",
        "Sent"
    )

if __name__ == "__main__":
    main()