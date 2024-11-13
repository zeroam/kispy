import requests

from kispy.auth import KisAuth
from kispy.constants import REAL_URL, VIRTUAL_URL
from kispy.rate_limit import RateLimiter
from kispy.responses import BaseResponse


class BaseAPI:
    def __init__(self, auth: KisAuth):
        self._url = REAL_URL if auth.is_real else VIRTUAL_URL
        self._auth = auth

    def _request(self, method: str, url: str, **kwargs) -> BaseResponse:
        """공통 request 메서드"""
        RateLimiter().wait_if_needed()
        resp = requests.request(method, url, **kwargs)
        custom_resp = BaseResponse(headers=dict(resp.headers), status_code=resp.status_code, json=resp.json())
        custom_resp.raise_for_status()
        return custom_resp
