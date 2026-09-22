from app.pipeline import DailyPipeline
from app.telegram.bot import TelegramBot
from app.telegram.formatter import Formatter
from app.supabase_database import SupabaseDatabase

def main():

    db = SupabaseDatabase()

    if not db.health_check():
        raise RuntimeError("Supabase connection failed")

    pipeline = DailyPipeline()

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