from __future__ import annotations

from .destination import LogDestination, LogEntry, LogLevel


class ConsoleDestination(LogDestination):
    ICON = {
        LogLevel.INFO: "ℹ️",
        LogLevel.SUCCESS: "✓",
        LogLevel.WARNING: "⚠",
        LogLevel.ERROR: "✗",
    }

    def write(self, entry: LogEntry) -> None:
        t = entry.time.strftime("%H:%M:%S")
        icon = self.ICON[entry.level]

        print(f"[{t}] {entry.component:<14} {icon} {entry.message}")
