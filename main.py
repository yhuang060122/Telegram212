from app.logger import log
from app.pipeline import DailyPipeline
from app.telegram.bot import TelegramBot
from app.telegram.formatter import Formatter


def main():
    pipeline = DailyPipeline()

    portfolio, analytics, report, history = pipeline.run()

    message = Formatter.daily(
        portfolio,
        analytics,
        report
    )

    TelegramBot().send(message)

    log.success(
        "Telegram",
        "Sent"
    )


if __name__ == "__main__":
    main()
