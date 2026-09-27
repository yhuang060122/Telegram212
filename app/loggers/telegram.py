from __future__ import annotations

import os

import requests

from app.telegram.bot import TelegramBot

from .destination import LogDestination, LogEntry


class TelegramDestination(LogDestination):
    def __init__(self):
        self.bot = TelegramBot()

    def write(self, entry: LogEntry) -> None:
        # 实时 log 不发送，由 Logger.flush() 统一发送
        return

    def send_summary(self, text: str) -> None:
        self.bot.send(text)
