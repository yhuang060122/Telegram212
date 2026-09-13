import os
import requests

class MacroCollector:

    BASE = "https://api.stlouisfed.org/fred/series/observations"

    SERIES = {
        "fed_rate": "FEDFUNDS",
        "us10y": "DGS10",
        "vix": "VIXCLS",
        "dxy": "DTWEXBGS",
    }

    def __init__(self):
        self.api_key = os.getenv("FRED_API_KEY")

    def _latest(self, series_id):

        r = requests.get(
            self.BASE,
            params={
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 1,
            },
            timeout=15
        )

        r.raise_for_status()

        obs = r.json()["observations"][0]

        return float(obs["value"])

    def collect(self):

        return {
            name: self._latest(code)
            for name, code in self.SERIES.items()
        }