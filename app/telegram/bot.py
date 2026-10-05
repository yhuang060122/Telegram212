import os

import requests


class TelegramBot:
    BASE = "https://api.telegram.org"

    def __init__(self):

        self.token = os.getenv("TG_BOT_TOKEN")
        self.chat_id = os.getenv("TG_CHAT_ID")
        self.forum_topics_id = os.getenv("TG_FORUM_TOPICS_ID")
        self.topic_logs_id = os.getenv("TG_TOPIC_LOGS_ID")
        self.topic_daily_id = os.getenv("TG_TOPIC_DAILY_ID")
        self.topic_market_close_id = os.getenv("TG_TOPIC_MARKET_CLOSE_ID")

    def send(self, text):
        url = f"{self.BASE}/bot{self.token}/sendMessage"

        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown"}

        r = requests.post(url, json=payload, timeout=10)

        if not r.ok:
            raise RuntimeError(
                f"Telegram sendMessage failed: {r.status_code} - {r.text}"
            )

        return r.json()

    def send_to_logs(self, text):
        self.__send_to_topic(text, self.topic_logs_id)

    def send_to_daily(self, text):
        self.__send_to_topic(text, self.topic_daily_id)

    def send_to_market_close(self, text):
        self.__send_to_topic(text, self.topic_market_close_id)

    def __send_to_topic(self, text, topic_id):
        url = f"{self.BASE}/bot{self.token}/sendMessage"

        payload = {
            "chat_id": self.forum_topics_id,
            "message_thread_id": topic_id,
            "text": text,
            "parse_mode": "Markdown",
        }
        r = requests.post(url, json=payload, timeout=10)

        if not r.ok:
            raise RuntimeError(
                f"Telegram Topic {topic_id} sendMessage failed: {r.status_code} - {r.text}"
            )

        return r.json()

    def get_updates(self, offset=None):
        url = f"{self.BASE}/bot{self.token}/getUpdates"

        params = {"timeout": 30}

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
