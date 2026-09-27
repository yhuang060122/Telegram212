from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class LogLevel(str, Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class LogEntry:
    time: datetime
    level: LogLevel
    component: str
    message: str


class LogDestination(ABC):
    @abstractmethod
    def write(self, entry: LogEntry) -> None: ...
