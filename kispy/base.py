from datetime import datetime
import logging
import time
from zoneinfo import ZoneInfo

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from kispy.auth import KisAuth
from kispy.constants import REAL_URL, VIRTUAL_URL
from kispy.err_codes import ErrorCode
from kispy.rate_limit import RateLimiter
from kispy.responses import BaseResponse

logger = logging.getLogger(__name__)


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
        while True:
            RateLimiter().wait_if_needed()
            resp = self._session.request(method, url, **kwargs)
            custom_resp = BaseResponse(headers=dict(resp.headers), status_code=resp.status_code, json=resp.json())
            if custom_resp.err_code == ErrorCode.TOO_MANY_REQUESTS:
                logger.warning("API 호출 횟수를 초과하였습니다.")
                time.sleep(0.1)
                continue
            custom_resp.raise_for_status()
            return custom_resp
        
    def _parse_date(self, date_str: str, zone_info: ZoneInfo | None = None) -> datetime:
        date_str = date_str.replace("-", "")
        try : 
            result = datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            result = datetime.strptime(date_str, "%Y%m%d%H%M%S")
        if zone_info:
            result = result.replace(tzinfo=zone_info)
        return result
