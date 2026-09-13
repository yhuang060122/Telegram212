from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

class Trading212Error(Exception):
    """Trading212 API Error"""

class Trading212Client:

    BASE_URL = {
        "live": "https://live.trading212.com/api/v0",
        "demo": "https://demo.trading212.com/api/v0",
    }

    def __init__(
            self,
            api_key: str | None = None,
            api_secret: str | None = None,
            environment: str | None = None,
            timeout: float = 20.0,
    ) -> None:
        self.api_key = api_key or os.getenv("T212_API_KEY")
        self.api_secret = api_secret or os.getenv("T212_API_SECRET")

        env = (environment or os.getenv("T212_ENV", "live")).strip().lower()
        if env not in self.BASE_URL:
            raise ValueError(
                f"environment 必须是 {sorted(self.BASE_URL)} 之一，收到 {env!r}"
            )
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "缺少 Trading212 凭据：请在 .env 中设置 T212_API_KEY 和 T212_API_SECRET"
                "（API Secret 只在创建 key 时显示一次，丢了只能重新生成）"
            )

        self.environment = env
        self.base_url = self.BASE_URL[env]
        self.timeout = timeout

        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(
            self.api_key,
            self.api_secret
        )

    def _request(
            self,
            method: str,
            endpoint: str,
            **kwargs: Any
    ) -> Any:
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs
            )
        except requests.RequestException as exc:
            raise Trading212Error(f"{method} {url} 请求失败: {exc}") from exc

        if not response.ok:
            raise Trading212Error(self._error_message(response))

        if not response.text:
            return None

        try:
            return response.json()
        except ValueError as exc:
            raise Trading212Error(
                f"{response.url} 返回了非 JSON 内容: {response.text[:200]!r}"
            ) from exc

    @staticmethod
    def _error_message(response: requests.Response) -> str:
        message = f"{response.url} - {response.status_code} - {response.text}"

        if response.status_code == 401:
            message += (
                " | 认证失败：检查 .env 里填的是不是真实 API Key/Secret（不是占位值）、"
                "key 是否设置了 IP 白名单、以及 demo/live 环境是否与生成 key 的环境一致"
            )
        elif response.status_code == 429:
            message += " | 触发限流：参考响应头 x-ratelimit-reset 稍后重试"

        return message

    def account_summary(self) -> Any:
        return self._request(
            "GET",
            "/equity/account/summary",
        )

    def positions(self) -> Any:
        return self._request(
            "GET",
            "/equity/positions",
        )

    def instruments(self) -> Any:
        return self._request(
            "GET",
            "/equity/metadata/instruments",
        )

    def exchanges(self) -> Any:
        return self._request(
            "GET",
            "/equity/metadata/exchanges",
        )

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> Trading212Client:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
