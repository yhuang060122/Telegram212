import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

class Trading212Client:
    BASE_URL = "https://live.trading212.com/api/v0/equity"

    def __init__(self):
        api_key = os.getenv("T212_API_KEY")
        api_secret = os.getenv("T212_API_SECRET")

        if not api_key:
            raise ValueError("T212_API_KEY missing")

        if not api_secret:
            raise ValueError("T212_API_SECRET missing")

        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(
            api_key,
            api_secret
        )

    def _get(self, endpoint: str):
        url = f"{self.BASE_URL}/{endpoint}"
        r = self.session.get(url, timeout=20)
        r.raise_for_status()
        return r.json()

    def close(self) -> None:
        self.session.close()

    # -------------------------
    # Portfolio
    # -------------------------

    def account_summary(self) -> dict:
        return self._get("account/summary")

    def positions(self) -> list[dict]:
        return self._get("positions")

    # TODO:
    # def instrument(self, ticker: str) -> dict:
    #     return self._get(f"metadata/instruments/{ticker}")

