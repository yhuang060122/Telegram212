from app.pipeline import DailyPipeline
from app.telegram.bot import TelegramBot
from app.telegram.formatter import Formatter
import os

pipeline = DailyPipeline()

portfolio, report, history = pipeline.run()

message = Formatter.market_close(
    portfolio=portfolio,
    report=report,
    history=history
)

TelegramBot().send(message)

print("✅ Market close report sent.")