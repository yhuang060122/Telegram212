import os

import requests
from dotenv import load_dotenv

from app.domain.macro import MacroData
from app.logger import log

load_dotenv()


class FredClient:

    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    SERIES = {
        "fed_rate": "FEDFUNDS",
        "us10y": "DGS10",
        "vix": "VIXCLS",
        "dxy": "DTWEXBGS",
    }

    def __init__(self):

        self.api_key = os.getenv("FRED_API_KEY")

        if not self.api_key:
            raise ValueError("FRED_API_KEY missing")

    def _latest(self, series_id: str):

        try:
            r = requests.get(
                self.BASE_URL,
                params={
                    "series_id": series_id,
                    "api_key": self.api_key,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": 1,
                },
                timeout=20,
            )

            r.raise_for_status()

            log.success(
                "Macro",
                f"{series_id} data"
            )

            obs = r.json()["observations"][0]["value"]

            # FRED 缺失值通常是 "."
            if obs in (".", "", None):
                log.warning(
                    "Macro",
                    f"{series_id} data missing"
                )
                return None

            log.success(
                "Macro",
                f"{series_id} value: {obs}"
            )

            return float(obs)

        except Exception as e:
            log.error(
                "Macro",
                str(e)
            )
            return None

    def snapshot(self) -> MacroData:

        return MacroData(
            fed_rate=self._latest("FEDFUNDS"),
            us10y=self._latest("DGS10"),
            vix=self._latest("VIXCLS"),
            dxy=self._latest("DTWEXBGS"),
        )