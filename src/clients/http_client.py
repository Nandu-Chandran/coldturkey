import requests
from utils.retry import retry
from utils.config import load_config

cfg = load_config()
BASE = cfg['base_url']

class HTTPBinClient:
    def __init__(self, base_url=BASE, timeout=5):
        self.base_url = base_url
        self.timeout = timeout

    @retry(attempts=3, backoff_seconds=1, allowed_exceptions=(requests.RequestException,))
    def get(self, path="/get", params=None, headers=None):
        url = self.base_url.rstrip("/") + path
        resp = requests.get(url, params=params, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp

    @retry(attempts=3, backoff_seconds=1, allowed_exceptions=(requests.RequestException,))
    def post(self, path="/post", json=None, data=None, headers=None):
        url = self.base_url.rstrip("/") + path
        resp = requests.post(url, json=json, data=data, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp

