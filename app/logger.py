import logging
import sys

class PipelineLogger:

    def __init__(self):
        self.logger = logging.getLogger("telegram212")

        if self.logger.handlers:
            return

        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(
            "[%(asctime)s] %(message)s",
            datefmt="%H:%M:%S",
        )

        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def info(self, module: str, message: str):
        self.logger.info(
            f"{module:<12} - {message}"
        )

    def success(self, module: str, message: str):
        self.logger.info(
            f"{module:<12} ✓ {message}"
        )

    def warning(self, module: str, message: str):
        self.logger.warning(
            f"{module:<12} ⚠ {message}"
        )

    def error(self, module: str, message: str):
        self.logger.error(
            f"{module:<12} ✗ {message}"
        )

log = PipelineLogger()