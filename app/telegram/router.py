from .formatter import Formatter
from .handlers import (
    daily,
    portfolio,
    risk,
    history,
    analyze_stock
)


class CommandRouter:

    def dispatch(self, text):

        parts = text.strip().split()
        cmd = parts[0].lower()

        if cmd == "/daily":
            return daily()

        elif cmd == "/portfolio":
            return portfolio()

        elif cmd == "/risk":
            return risk()

        elif cmd == "/history":
            return history(text)

        elif cmd == "/help":
            return Formatter.help()

        elif cmd == "/start":
            return Formatter.help()

        # elif cmd == "/performance":
        #     return performance()

        elif cmd == "/stock":
            if len(parts) < 2:
                return "Usage: `/stock NVDA`"
            return analyze_stock(parts[1])

        return "Unknown command."
