import os
from datetime import datetime
from decimal import Decimal
from time import sleep

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

from app.domain.cashflow import CashFlow, CashFlowType
from app.logger import log

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

    def _get(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{self.BASE_URL}/{endpoint}"

        while True:
            r = self.session.get(url, params=params, timeout=20)

            if r.status_code != 200:
                log.error("Trading212",
                          f"Code: {r.status_code}, URL: {r.request.url}, Body: {r.text}")

            if r.status_code == 429:
                retry = int(r.headers.get("Retry-After", 60))
                sleep(retry)
                continue

            log.success("Trading212",
                        f"Code: {r.status_code}, URL: {r.request.url}")

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

    def transactions(self) -> list[CashFlow]:

        endpoint = "history/transactions"

        params = {
            "limit": 50,
        }

        cashflows = []
        requests_count = 0

        while True:

            data = self._get(endpoint, params)

            cashflows.extend(
                self._to_cashflow(i)
                for i in data["items"]
            )

            # '/api/v0/equity/history/transactions?limit=50&cursor=01a083bf-7680-7472-8f69-581cef84b88c&time=2026-09-09T01:19:18.138Z'
            next_page = data.get("nextPagePath")
            if not next_page:
                break

            endpoint = str(next_page).replace("/api/v0/equity/", "")
            params = None

            requests_count += 1

            # Trading212: 6 req / minute
            if requests_count >= 5:
                # sleep(60)
                break
                requests_count = 0
            else:
                sleep(10)

        return sorted(
            cashflows,
            key=lambda x: x.datetime,
        )

    @staticmethod
    def _to_cashflow(item: dict) -> CashFlow:

        tx_type = item["type"]

        amount = Decimal(str(item["amount"]))

        if tx_type == "DEPOSIT":
            amount = -amount

        elif tx_type == "WITHDRAW":
            amount = amount

        elif tx_type == "FEE":
            amount = -amount

        elif tx_type in (
                "INTEREST_ON_FREE_CASH",
                "LENDING_INTEREST",
        ):
            amount = amount

        elif tx_type == "TRANSFER":
            amount = Decimal("0")

        mapping = {
            "DEPOSIT": CashFlowType.DEPOSIT,
            "WITHDRAW": CashFlowType.WITHDRAWAL,
            "FEE": CashFlowType.FEE,
            "TRANSFER": CashFlowType.TRANSFER,
            "INTEREST_ON_FREE_CASH": CashFlowType.INTEREST,
            "LENDING_INTEREST": CashFlowType.INTEREST,
        }

        return CashFlow(
            reference=item["reference"],
            datetime=datetime.fromisoformat(
                item["dateTime"].replace("Z", "+00:00")
            ),
            amount=amount,
            currency=item["currency"],
            type=mapping[tx_type],
        )
