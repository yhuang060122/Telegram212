import logging
import requests


logger = logging.getLogger(__name__)

class CollectorError(Exception):
    pass

class BaseCollector:

    def safe_get(self, url: str, params: dict):
        try:
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            return r.json()
        except requests.HTTPError as e:
            logger.warning(
                "HTTP %s : %s",
                e.response.status_code,
                url
            )
            raise CollectorError(str(e))
        except requests.RequestException as e:
            logger.warning("Network error: %s", e)
            raise CollectorError(str(e))