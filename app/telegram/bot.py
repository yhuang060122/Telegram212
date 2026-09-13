import os
import requests

class TelegramBot:

    BASE = "https://api.telegram.org"

    def __init__(self):

        self.token = os.getenv("TG_BOT_TOKEN")
        self.chat_id = os.getenv("TG_CHAT_ID")

    def send(self, text):
        url = f"{self.BASE}/bot{self.token}/sendMessage"

        r = requests.post(
            url,
            json={
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
        )

        r.raise_for_status()
        return r.json()

    def get_updates(self, offset=None):
        url = f"{self.BASE}/bot{self.token}/getUpdates"

        params = {
            "timeout": 30
        }

        if offset:
            params["offset"] = offset

        r = requests.get(url, params=params, timeout=35)

        r.raise_for_status()
        return r.json()["result"]

    def health_check(self):
        url = f"{self.BASE}/bot{self.token}/getMe"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()