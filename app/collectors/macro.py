import os

from app.collectors.base import BaseCollector, CollectorError
from app.logger import log

class MacroCollector(BaseCollector):

    BASE = "https://api.stlouisfed.org/fred/series/observations"

    SERIES = {
        "fed_rate": "FEDFUNDS",
        "us10y": "DGS10",
        "vix": "VIXCLS",
        "dxy": "DTWEXBGS",
    }

    DEFAULT = {
        "fed_rate": None,
        "us10y": None,
        "vix": None,
        "dxy": None,
    }

    def __init__(self):
        self.api_key = os.getenv("FRED_API_KEY")

    def _latest(self, series_id: str):

        try:
            data = self.safe_get(
                self.BASE,
                {
                    "series_id": series_id,
                    "api_key": self.api_key,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": 1,
                },
            )

            log.success(
                "Macro",
                f"{series_id} data"
            )

            observations = data.get("observations", [])

            if not observations:
                return None

            value = observations[0]["value"]

            # FRED 缺失值通常是 "."
            if value in (".", "", None):
                log.warning(
                    "Macro",
                    f"{series_id} data missing"
                )
                return None

            log.success(
                "Macro",
                f"{series_id} value: {value}"
            )

            return float(value)

        except (CollectorError, ValueError, KeyError, IndexError) as e:
            log.error(
                "Macro",
                str(e)
            )
            return None

    def collect(self):

        result = {}

        for name, code in self.SERIES.items():
            result[name] = self._latest(code)

        return result