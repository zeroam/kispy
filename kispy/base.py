import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from kispy.auth import KisAuth
from kispy.constants import REAL_URL, VIRTUAL_URL
from kispy.rate_limit import RateLimiter
from kispy.responses import BaseResponse


class BaseAPI:
    def __init__(self, auth: KisAuth):
        self._url = REAL_URL if auth.is_real else VIRTUAL_URL
        self._auth = auth

        retry_strategy = Retry(
            total=5,
            backoff_factor=0.5,
            backoff_jitter=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            respect_retry_after_header=True,
            raise_on_status=True,
            connect=3,
            read=3,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session = requests.Session()
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def _request(self, method: str, url: str, **kwargs) -> BaseResponse:
        """공통 request 메서드"""
        RateLimiter().wait_if_needed()
        resp = self._session.request(method, url, **kwargs)
        custom_resp = BaseResponse(headers=dict(resp.headers), status_code=resp.status_code, json=resp.json())
        custom_resp.raise_for_status()
        return custom_resp
