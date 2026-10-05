from app.logger import log
from app.pipeline import DailyPipeline
from app.telegram.bot import TelegramBot
from app.telegram.formatter import Formatter

pipeline = DailyPipeline()

portfolio, analytics, report, history = pipeline.run()

message = Formatter.market_close(portfolio=portfolio, report=report, history=history)

bot = TelegramBot()
bot.send(message)
bot.send_to_market_close(message)

log.success("✅ Market close report", "Sent")
