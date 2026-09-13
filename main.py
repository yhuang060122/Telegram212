from app.pipeline import DailyPipeline
from app.telegram.bot import TelegramBot
from app.telegram.formatter import Formatter

def main():

    pipeline = DailyPipeline()

    portfolio, report = pipeline.run()

    bot = TelegramBot()

    message = Formatter.daily(
        portfolio,
        report
    )

    bot.send(message)

    print("✅ Daily report sent.")

if __name__ == "__main__":
    main()