from __future__ import annotations

import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from app.loggers.console import ConsoleDestination
from app.loggers.destination import (
    LogEntry,
    LogLevel,
)
from app.loggers.telegram import TelegramDestination

load_dotenv()


class Logger:
    ICON = {
        LogLevel.INFO: "ℹ️",
        LogLevel.SUCCESS: "✅",
        LogLevel.WARNING: "⚠️",
        LogLevel.ERROR: "❌",
    }

    def __init__(self):

        self.console = ConsoleDestination()

        self.telegram = None
        if os.getenv("ENABLE_TELEGRAM_LOG", "false").lower() == "true":
            self.telegram = TelegramDestination()

        self.entries: list[LogEntry] = []
        self.started_at = datetime.now(timezone.utc)

        self.failed = False

    def _log(
        self,
        level: LogLevel,
        component: str,
        message: str,
    ) -> None:

        entry = LogEntry(
            time=datetime.now(timezone.utc),
            level=level,
            component=component,
            message=message,
        )

        self.entries.append(entry)

        self.console.write(entry)

    def info(self, component: str, message: str):
        self._log(LogLevel.INFO, component, message)

    def success(self, component: str, message: str):
        self._log(LogLevel.SUCCESS, component, message)

    def warning(self, component: str, message: str):
        self._log(LogLevel.WARNING, component, message)

    def error(self, component: str, message: str):
        self._log(LogLevel.ERROR, component, message)

    def flush(self, title: str = "Daily Pipeline"):

        if self.telegram is None:
            return

        duration = (datetime.now(timezone.utc) - self.started_at).total_seconds()

        header = f"❌ *{title} Failed*" if self.failed else f"📊 *{title} Completed*"

        lines = [header, ""]

        for entry in self.entries:
            t = entry.time.strftime("%H:%M")
            icon = self.ICON[entry.level]

            lines.append(f"`{t}` {icon} *{entry.component}*")
            lines.append(entry.message)
            lines.append("")

        lines.append("---")
        lines.append(f"⏱ Duration: `{duration:.1f}s`")

        self.telegram.send_summary("\n".join(lines))

        self.entries.clear()
        self.failed = False
        self.started_at = datetime.now(timezone.utc)


log = Logger()
